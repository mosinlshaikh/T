from __future__ import annotations

from dataclasses import asdict, dataclass, field


@dataclass(frozen=True)
class StrategyCatalogItem:
    name: str
    family: str
    purpose: str
    required_data: list[str]
    output: str = "BUY / SELL / HOLD / SKIP"
    status: str = "PAPER_ADVISORY"
    safety_rules: list[str] = field(
        default_factory=lambda: [
            "Evidence required",
            "No single-signal trading",
            "No fake whale/news claims",
            "Risk engine must approve",
            "Zero-hallucination gate must verify",
            "Live execution unavailable in this build",
        ]
    )


BINANCE_SPOT_STRATEGY_CATALOG: tuple[StrategyCatalogItem, ...] = (
    StrategyCatalogItem(
        "MULTI_TIMEFRAME_TREND_ALIGNMENT",
        "Candle / Structure",
        "Align 1m, 5m, 15m, 1h, and 4h trend context before allowing confidence to rise.",
        ["candles_1m", "candles_5m", "candles_15m", "candles_1h", "candles_4h"],
    ),
    StrategyCatalogItem(
        "BREAKOUT_RETEST_CONFIRMATION",
        "Candle / Structure",
        "Require breakout, retest, volume confirmation, and support/resistance evidence.",
        ["candles", "volume", "support_resistance", "market_price"],
    ),
    StrategyCatalogItem(
        "REVERSAL_WICK_REJECTION",
        "Candle / Structure",
        "Detect wick rejection near support/resistance with confirmation candles.",
        ["candles", "wick_rejection", "support_resistance", "volume"],
    ),
    StrategyCatalogItem(
        "ORDER_BOOK_IMBALANCE_SCALPER",
        "Order Book",
        "Score bid/ask imbalance, spread risk, walls, and liquidity gaps for paper-only intent.",
        ["order_book_bids", "order_book_asks", "spread", "liquidity_gap"],
    ),
    StrategyCatalogItem(
        "LIQUIDITY_WALL_FAKEOUT_FILTER",
        "Order Book",
        "Mark suspicious buy/sell walls and reduce confidence when walls look unsupported.",
        ["order_book_depth", "wall_history", "trade_tape"],
    ),
    StrategyCatalogItem(
        "VOLUME_SPIKE_WITH_STRUCTURE",
        "Volume",
        "Require abnormal volume plus candle/structure agreement before signal is considered.",
        ["volume_24h", "recent_volume", "candles", "market_structure"],
    ),
    StrategyCatalogItem(
        "WHALE_TRADE_CONFIRMATION",
        "Whale",
        "Use large public trades only when timestamped evidence exists; missing whale data returns SKIP.",
        ["large_public_trades", "trade_notional", "timestamp", "source"],
    ),
    StrategyCatalogItem(
        "FAKE_WHALE_MOVEMENT_FILTER",
        "Whale",
        "Reduce confidence when large movement lacks follow-through, volume, or order-book support.",
        ["large_public_trades", "volume_follow_through", "order_book_confirmation"],
    ),
    StrategyCatalogItem(
        "NEWS_RISK_EMERGENCY_FILTER",
        "News / Risk",
        "Force HOLD/SKIP when listing, delisting, regulatory, or negative emergency risk is present.",
        ["news_source", "news_timestamp", "risk_flag", "sentiment"],
    ),
    StrategyCatalogItem(
        "BINANCE_ANNOUNCEMENT_WATCH",
        "News / Exchange",
        "Watch Binance announcement adapter evidence without inventing unsupported news.",
        ["announcement_source", "published_at", "symbol_match"],
    ),
    StrategyCatalogItem(
        "SUPPORT_RESISTANCE_ZONE_REACTION",
        "Market Structure",
        "Score price behavior around support, resistance, liquidity zones, and range/trend state.",
        ["support", "resistance", "liquidity_zone", "candles"],
    ),
    StrategyCatalogItem(
        "VOLATILITY_REGIME_GUARD",
        "Risk / Structure",
        "Lower trade readiness when volatility regime is high or uncertain.",
        ["atr_or_range_proxy", "candles", "spread", "risk_score"],
    ),
    StrategyCatalogItem(
        "RISK_FIRST_POSITION_FILTER",
        "Risk",
        "Block trade intent unless reserve, exposure, cooldown, stop-loss, and take-profit rules pass.",
        ["wallet_snapshot", "risk_context", "stop_loss", "take_profit"],
    ),
    StrategyCatalogItem(
        "LOCAL_AI_CONFIDENCE_CALIBRATION",
        "Local AI",
        "Use persisted paper outcomes to calibrate confidence without external AI keys.",
        ["paper_decisions", "paper_journal", "risk_blocks", "audit_events"],
    ),
    StrategyCatalogItem(
        "MULTI_FACTOR_MASTER_COMBINER",
        "Composite",
        "Combine candle, order book, whale, news, structure, local AI, and risk signals.",
        [
            "candle_signal",
            "order_book_signal",
            "whale_signal",
            "news_risk_signal",
            "market_structure_signal",
            "risk_result",
        ],
    ),
)


def strategy_catalog_payload() -> dict[str, object]:
    return {
        "mode": "paper_advisory_only",
        "exchange_scope": "Binance Spot public-market and paper-trading architecture",
        "live_execution_available": False,
        "withdrawals_supported": False,
        "external_ai_key_required": False,
        "strategy_count": len(BINANCE_SPOT_STRATEGY_CATALOG),
        "families": sorted({item.family for item in BINANCE_SPOT_STRATEGY_CATALOG}),
        "strategies": [asdict(item) for item in BINANCE_SPOT_STRATEGY_CATALOG],
        "master_rules": [
            "No Data = No Trade",
            "No Proof = No Decision",
            "Conflicts = HOLD/SKIP",
            "Low confidence = SKIP",
            "News risk high = HOLD/SKIP",
            "Risk unsafe = SKIP",
            "No live order placement in this build",
        ],
    }
