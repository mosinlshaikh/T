from __future__ import annotations

from dataclasses import dataclass

from trading_os.ai.decision_types import DecisionAction, EvidenceItem, EvidenceType
from trading_os.intelligence.types import IntelligenceSignal
from trading_os.market.candle_engine import Candle
from trading_os.market.timeframes import Timeframe, normalize_timeframe


@dataclass(frozen=True)
class MarketStructure:
    support: float
    resistance: float
    liquidity_zone_low: float
    liquidity_zone_high: float
    trend_structure: str
    higher_high: bool
    lower_low: bool
    range_vs_trend: str
    volatility_regime: str
    confidence_score: float


@dataclass
class MarketStructureEngine:
    min_candles: int = 5

    def analyze(
        self,
        symbol: str,
        timeframe: str | Timeframe,
        candles: list[Candle],
    ) -> IntelligenceSignal:
        tf = normalize_timeframe(timeframe)
        relevant = [candle for candle in candles if candle.symbol.upper() == symbol.upper()]
        if len(relevant) < self.min_candles:
            return IntelligenceSignal(
                name="market_structure",
                symbol=symbol.upper(),
                timeframe=tf,
                direction=DecisionAction.SKIP,
                confidence=0.0,
                missing_data=["market_structure_candles"],
                reason="Missing candles for market structure analysis.",
            )

        structure = self._structure(relevant)
        direction = DecisionAction.HOLD
        if structure.trend_structure == "bullish" and structure.higher_high:
            direction = DecisionAction.BUY
        elif structure.trend_structure == "bearish" and structure.lower_low:
            direction = DecisionAction.SELL

        evidence = [
            EvidenceItem(
                evidence_type=EvidenceType.CANDLE,
                source="market_structure",
                summary=(
                    f"support={structure.support}; resistance={structure.resistance}; "
                    f"trend_structure={structure.trend_structure}; range_vs_trend={structure.range_vs_trend}; "
                    f"volatility_regime={structure.volatility_regime}"
                ),
                confidence=structure.confidence_score,
                payload={
                    "support": structure.support,
                    "resistance": structure.resistance,
                    "liquidity_zone_low": structure.liquidity_zone_low,
                    "liquidity_zone_high": structure.liquidity_zone_high,
                    "higher_high": structure.higher_high,
                    "lower_low": structure.lower_low,
                    "range_vs_trend": structure.range_vs_trend,
                    "volatility_regime": structure.volatility_regime,
                },
            )
        ]
        return IntelligenceSignal(
            name="market_structure",
            symbol=symbol.upper(),
            timeframe=tf,
            direction=direction,
            confidence=structure.confidence_score,
            evidence=evidence,
            reason="Market structure analysis completed with candle evidence.",
        )

    def _structure(self, candles: list[Candle]) -> MarketStructure:
        highs = [candle.high for candle in candles]
        lows = [candle.low for candle in candles]
        closes = [candle.close for candle in candles]
        support = min(lows)
        resistance = max(highs)
        higher_high = highs[-1] > highs[-2] > highs[-3]
        lower_low = lows[-1] < lows[-2] < lows[-3]
        trend_structure = "bullish" if higher_high else "bearish" if lower_low else "neutral"
        price_range = resistance - support
        average_close = sum(closes) / len(closes)
        range_pct = price_range / max(average_close, 1e-9) * 100
        range_vs_trend = "trend" if higher_high or lower_low else "range"
        volatility_regime = "high" if range_pct > 3 else "medium" if range_pct > 1 else "low"
        confidence = 0.45
        confidence += 0.25 if range_vs_trend == "trend" else 0.0
        confidence += 0.15 if volatility_regime in {"medium", "high"} else 0.0
        return MarketStructure(
            support=round(support, 8),
            resistance=round(resistance, 8),
            liquidity_zone_low=round(support + price_range * 0.2, 8),
            liquidity_zone_high=round(resistance - price_range * 0.2, 8),
            trend_structure=trend_structure,
            higher_high=higher_high,
            lower_low=lower_low,
            range_vs_trend=range_vs_trend,
            volatility_regime=volatility_regime,
            confidence_score=round(min(confidence, 1.0), 4),
        )
