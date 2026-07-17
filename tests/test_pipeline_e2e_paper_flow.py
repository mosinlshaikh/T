import json
from pathlib import Path

from trading_os.ai.decision_types import EvidenceItem, EvidenceType
from trading_os.config import TradingOSConfig
from trading_os.market.candle_engine import Candle
from trading_os.market.order_book_engine import OrderBookLevel, OrderBookSnapshot
from trading_os.market.timeframes import Timeframe
from trading_os.orchestrator import TradingOSBackend
from trading_os.pipeline.decision_to_trade_types import PipelineInput, PipelineResult


def test_e2e_paper_pipeline_opens_trade_and_writes_audit_events(tmp_path: Path) -> None:
    audit_path = tmp_path / "audit.jsonl"
    backend = TradingOSBackend(
        config=TradingOSConfig(
            database_url=f"sqlite:///{tmp_path / 'trading.sqlite3'}",
            audit_log_path=str(audit_path),
        )
    )

    result = backend.decision_to_trade_pipeline.run(
        PipelineInput(
            symbol="BTCUSDT",
            timeframe=Timeframe.FIVE_MINUTES,
            market_price=105.0,
            quantity=0.1,
            stop_loss=101.0,
            take_profit=112.0,
            account_balance=10_000.0,
            candles=_bullish_candles(),
            order_book=_bullish_order_book(),
        ),
        [
            EvidenceItem(
                EvidenceType.MARKET_TICK,
                "unit_test_market_tick",
                "Mock public market tick for paper-only pipeline regression.",
                1.0,
            )
        ],
    )

    assert result.status == "PAPER_OPEN"
    assert result.decision.action.value == "BUY"
    assert result.decision.verified_decision is True
    assert result.execution_intent is not None
    assert result.execution_intent.live_enabled is False
    assert result.paper_fill is not None
    assert backend.portfolio.open_positions

    stage_names = [stage["stage"] for stage in result.stage_results]
    assert stage_names == [
        "shutdown_gate",
        "market_intelligence",
        "combined_signal",
        "strategy_signal",
        "risk",
        "ai_decision",
        "zero_hallucination",
        "trade_lifecycle",
        "execution_intent",
        "paper_execution",
    ]

    events = _audit_event_types(audit_path)
    assert "ai_decision" in events
    assert "execution_intent_created" in events
    assert "paper_order_fill" in events
    assert "portfolio_snapshot" in events
    assert "decision_to_trade_pipeline_result" in events


def test_e2e_missing_core_market_data_skips_without_intent_or_fill(tmp_path: Path) -> None:
    audit_path = tmp_path / "audit.jsonl"
    backend = TradingOSBackend(
        config=TradingOSConfig(
            database_url=f"sqlite:///{tmp_path / 'trading.sqlite3'}",
            audit_log_path=str(audit_path),
        )
    )

    result = backend.decision_to_trade_pipeline.run(
        PipelineInput(
            symbol="BTCUSDT",
            timeframe=Timeframe.FIVE_MINUTES,
            market_price=105.0,
            quantity=0.1,
            stop_loss=101.0,
            take_profit=112.0,
            account_balance=10_000.0,
            candles=None,
            order_book=None,
            whale_trades=None,
            news_items=None,
        ),
        [
            EvidenceItem(
                EvidenceType.MARKET_TICK,
                "unit_test_market_tick",
                "Mock public market tick with missing market intelligence data.",
                1.0,
            )
        ],
    )

    assert result.status == "SKIP"
    assert result.decision.action.value == "SKIP"
    assert result.execution_intent is None
    assert result.paper_fill is None
    assert backend.portfolio.open_positions == {}

    stage_by_name = {stage["stage"]: stage for stage in result.stage_results}
    assert stage_by_name["combined_signal"]["reason_code"] == "INSUFFICIENT_EVIDENCE"
    assert "candles" in stage_by_name["combined_signal"]["missing_data"]
    assert "order_book" in stage_by_name["combined_signal"]["missing_data"]
    assert "market_structure_candles" in stage_by_name["combined_signal"]["missing_data"]

    events = _audit_event_types(audit_path)
    assert "skipped_trade" in events
    assert "execution_intent_created" not in events
    assert "paper_order_fill" not in events


def test_e2e_missing_optional_whale_and_news_do_not_create_fake_claims(tmp_path: Path) -> None:
    audit_path = tmp_path / "audit.jsonl"
    backend = TradingOSBackend(
        config=TradingOSConfig(
            database_url=f"sqlite:///{tmp_path / 'trading.sqlite3'}",
            audit_log_path=str(audit_path),
        )
    )

    result = backend.decision_to_trade_pipeline.run(
        PipelineInput(
            symbol="BTCUSDT",
            timeframe=Timeframe.FIVE_MINUTES,
            market_price=105.0,
            quantity=0.1,
            stop_loss=101.0,
            take_profit=112.0,
            account_balance=10_000.0,
            candles=_bullish_candles(),
            order_book=_bullish_order_book(),
            whale_trades=None,
            news_items=None,
        ),
        [
            EvidenceItem(
                EvidenceType.MARKET_TICK,
                "unit_test_market_tick",
                "Mock public market tick for optional data safety check.",
                1.0,
            )
        ],
    )

    assert result.status == "PAPER_OPEN"
    assert result.execution_intent is not None
    assert result.paper_fill is not None

    evidence_types = {item.evidence_type for item in result.decision.evidence}
    assert EvidenceType.WHALE_SIGNAL not in evidence_types
    assert EvidenceType.NEWS_SIGNAL not in evidence_types

    events = _audit_events(audit_path)
    missing_events = [
        event["payload"]
        for event in events
        if event["event_type"] in {"whale_analysis", "news_risk_analysis"}
    ]
    assert any(payload["missing_data"] == ["whale_trades"] for payload in missing_events)
    assert any(payload["missing_data"] == ["news_source"] for payload in missing_events)


def test_e2e_missing_stop_loss_is_rejected_before_intent_or_fill(tmp_path: Path) -> None:
    result, audit_path, backend = _run_bullish_risk_case(
        tmp_path,
        quantity=0.1,
        stop_loss=0.0,
        take_profit=112.0,
    )

    _assert_risk_rejected_without_execution(result, backend)
    assert result.trade_context is not None
    assert "Stop-loss is required." in result.trade_context.risk_info.rejections
    assert "risk_rejection" in _audit_event_types(audit_path)


def test_e2e_missing_take_profit_is_rejected_before_intent_or_fill(tmp_path: Path) -> None:
    result, audit_path, backend = _run_bullish_risk_case(
        tmp_path,
        quantity=0.1,
        stop_loss=101.0,
        take_profit=0.0,
    )

    _assert_risk_rejected_without_execution(result, backend)
    assert result.trade_context is not None
    assert "Take-profit is required." in result.trade_context.risk_info.rejections
    assert "risk_rejection" in _audit_event_types(audit_path)


def test_e2e_oversized_trade_is_rejected_before_intent_or_fill(tmp_path: Path) -> None:
    result, audit_path, backend = _run_bullish_risk_case(
        tmp_path,
        quantity=10.0,
        stop_loss=101.0,
        take_profit=112.0,
    )

    _assert_risk_rejected_without_execution(result, backend)
    assert result.trade_context is not None
    assert (
        "Requested trade size exceeds max trade size." in result.trade_context.risk_info.rejections
    )
    assert "risk_rejection" in _audit_event_types(audit_path)


def _bullish_candles() -> list[Candle]:
    return [
        Candle("BTCUSDT", Timeframe.FIVE_MINUTES, 100.0, 101.0, 99.5, 100.5, 100.0, 1, 2),
        Candle("BTCUSDT", Timeframe.FIVE_MINUTES, 100.5, 102.0, 100.0, 101.5, 105.0, 2, 3),
        Candle("BTCUSDT", Timeframe.FIVE_MINUTES, 101.5, 103.0, 101.0, 102.5, 110.0, 3, 4),
        Candle("BTCUSDT", Timeframe.FIVE_MINUTES, 102.5, 104.0, 102.0, 103.5, 115.0, 4, 5),
        Candle("BTCUSDT", Timeframe.FIVE_MINUTES, 103.5, 106.0, 103.0, 105.0, 160.0, 5, 6),
    ]


def _bullish_order_book() -> OrderBookSnapshot:
    return OrderBookSnapshot(
        symbol="BTCUSDT",
        bids=[
            OrderBookLevel(price=104.99, quantity=120.0),
            OrderBookLevel(price=104.95, quantity=110.0),
            OrderBookLevel(price=104.90, quantity=100.0),
        ],
        asks=[
            OrderBookLevel(price=105.01, quantity=25.0),
            OrderBookLevel(price=105.05, quantity=20.0),
            OrderBookLevel(price=105.10, quantity=15.0),
        ],
        source="unit_test_order_book",
    )


def _audit_event_types(path: Path) -> list[str]:
    return [event["event_type"] for event in _audit_events(path)]


def _audit_events(path: Path) -> list[dict[str, object]]:
    return [
        json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()
    ]


def _run_bullish_risk_case(
    tmp_path: Path,
    *,
    quantity: float,
    stop_loss: float,
    take_profit: float,
) -> tuple[PipelineResult, Path, TradingOSBackend]:
    audit_path = tmp_path / "audit.jsonl"
    backend = TradingOSBackend(
        config=TradingOSConfig(
            database_url=f"sqlite:///{tmp_path / 'trading.sqlite3'}",
            audit_log_path=str(audit_path),
        )
    )
    result = backend.decision_to_trade_pipeline.run(
        PipelineInput(
            symbol="BTCUSDT",
            timeframe=Timeframe.FIVE_MINUTES,
            market_price=105.0,
            quantity=quantity,
            stop_loss=stop_loss,
            take_profit=take_profit,
            account_balance=10_000.0,
            candles=_bullish_candles(),
            order_book=_bullish_order_book(),
        ),
        [
            EvidenceItem(
                EvidenceType.MARKET_TICK,
                "unit_test_market_tick",
                "Mock public market tick for risk rejection regression.",
                1.0,
            )
        ],
    )
    return result, audit_path, backend


def _assert_risk_rejected_without_execution(
    result: PipelineResult,
    backend: TradingOSBackend,
) -> None:
    assert result.status == "REJECTED_BY_RISK"
    assert result.execution_intent is None
    assert result.paper_fill is None
    assert backend.portfolio.open_positions == {}

    stage_by_name = {stage["stage"]: stage for stage in result.stage_results}
    assert stage_by_name["risk"]["reason_code"] == "RISK_REJECTED"
    assert stage_by_name["execution_intent"]["reason_code"] == "NO_EXECUTION_INTENT"
    assert stage_by_name["paper_execution"]["reason_code"] == "NO_EXECUTION_INTENT"
