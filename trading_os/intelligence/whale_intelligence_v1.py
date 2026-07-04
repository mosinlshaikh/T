from __future__ import annotations

from dataclasses import dataclass

from trading_os.ai.decision_types import DecisionAction, EvidenceItem, EvidenceType
from trading_os.intelligence.types import IntelligenceSignal
from trading_os.market.timeframes import Timeframe, normalize_timeframe


@dataclass(frozen=True)
class WhaleTrade:
    symbol: str
    side: str
    quantity: float
    price: float
    timestamp: str
    source: str

    @property
    def notional(self) -> float:
        return self.quantity * self.price


@dataclass
class WhaleIntelligenceV1:
    large_trade_notional: float = 100_000.0
    volume_spike_ratio: float = 2.0

    def analyze(
        self,
        symbol: str,
        timeframe: str | Timeframe,
        trades: list[WhaleTrade] | None,
        average_volume: float | None = None,
    ) -> IntelligenceSignal:
        tf = normalize_timeframe(timeframe)
        if not trades:
            return IntelligenceSignal(
                name="whale_intelligence_v1",
                symbol=symbol.upper(),
                timeframe=tf,
                direction=DecisionAction.SKIP,
                confidence=0.0,
                missing_data=["whale_trades"],
                reason="Whale data missing; no whale signal generated.",
            )

        large = [trade for trade in trades if trade.notional >= self.large_trade_notional]
        total_volume = sum(trade.quantity for trade in trades)
        spike = bool(
            average_volume
            and average_volume > 0
            and total_volume >= average_volume * self.volume_spike_ratio
        )
        fake_filter = self._fake_whale_filter(large)
        buy_notional = sum(trade.notional for trade in large if trade.side.upper() == "BUY")
        sell_notional = sum(trade.notional for trade in large if trade.side.upper() == "SELL")
        direction = DecisionAction.HOLD
        if buy_notional > sell_notional and not fake_filter:
            direction = DecisionAction.BUY
        elif sell_notional > buy_notional and not fake_filter:
            direction = DecisionAction.SELL

        confidence = 0.35
        confidence += 0.25 if large else 0.0
        confidence += 0.2 if spike else 0.0
        confidence -= 0.25 if fake_filter else 0.0
        evidence = [
            EvidenceItem(
                evidence_type=EvidenceType.WHALE_SIGNAL,
                source="whale_intelligence_v1",
                summary=(
                    f"large_trades={len(large)}; volume_spike={spike}; "
                    f"fake_whale_filter={fake_filter}; buy_notional={round(buy_notional, 2)}; "
                    f"sell_notional={round(sell_notional, 2)}"
                ),
                confidence=round(max(min(confidence, 1.0), 0.0), 4),
                payload={
                    "large_trade_count": len(large),
                    "volume_spike": spike,
                    "fake_whale_filter": fake_filter,
                    "exchange_activity_signal": "placeholder",
                },
            )
        ]
        return IntelligenceSignal(
            name="whale_intelligence_v1",
            symbol=symbol.upper(),
            timeframe=tf,
            direction=direction,
            confidence=evidence[0].confidence,
            evidence=evidence,
            reason="Whale analysis completed with provided trade evidence.",
            risk_score=0.4 if fake_filter else 0.0,
        )

    @staticmethod
    def _fake_whale_filter(trades: list[WhaleTrade]) -> bool:
        if len(trades) < 2:
            return False
        sides = {trade.side.upper() for trade in trades}
        return len(sides) > 1
