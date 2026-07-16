from __future__ import annotations

from dataclasses import dataclass

from trading_os.ai.decision_types import DecisionAction, EvidenceItem, EvidenceType
from trading_os.intelligence.types import IntelligenceSignal
from trading_os.market.candle_engine import Candle
from trading_os.market.timeframes import Timeframe, normalize_timeframe


@dataclass(frozen=True)
class CandlePatternResult:
    trend: str
    breakout: bool
    reversal: bool
    wick_rejection: bool
    engulfing: bool
    volume_confirmed: bool
    confidence_score: float


@dataclass
class CandleIntelligenceEngine:
    min_candles: int = 3
    volume_confirmation_ratio: float = 1.2

    def analyze(
        self,
        symbol: str,
        timeframe: str | Timeframe,
        candles: list[Candle],
    ) -> IntelligenceSignal:
        tf = normalize_timeframe(timeframe)
        relevant = [candle for candle in candles if candle.symbol.upper() == symbol.upper()]
        if len(relevant) < self.min_candles:
            return self._missing(symbol, tf, "candles")

        result = self._patterns(relevant)
        direction = self._direction(result)
        evidence = [
            EvidenceItem(
                evidence_type=EvidenceType.CANDLE,
                source="candle_intelligence",
                summary=(
                    f"trend={result.trend}; breakout={result.breakout}; "
                    f"reversal={result.reversal}; wick_rejection={result.wick_rejection}; "
                    f"engulfing={result.engulfing}; volume_confirmed={result.volume_confirmed}"
                ),
                confidence=result.confidence_score,
                payload={
                    "trend": result.trend,
                    "breakout": result.breakout,
                    "reversal": result.reversal,
                    "wick_rejection": result.wick_rejection,
                    "engulfing": result.engulfing,
                    "volume_confirmed": result.volume_confirmed,
                },
            )
        ]
        return IntelligenceSignal(
            name="candle_intelligence",
            symbol=symbol.upper(),
            timeframe=tf,
            direction=direction,
            confidence=result.confidence_score,
            evidence=evidence,
            reason="Candle analysis completed with evidence.",
        )

    def _patterns(self, candles: list[Candle]) -> CandlePatternResult:
        last = candles[-1]
        prev = candles[-2]
        closes = [candle.close for candle in candles]
        volumes = [candle.volume for candle in candles[:-1]]
        average_volume = sum(volumes) / len(volumes) if volumes else 0.0
        volume_confirmed = (
            average_volume > 0 and last.volume >= average_volume * self.volume_confirmation_ratio
        )
        trend = self._trend(closes)
        breakout = last.close > max(candle.high for candle in candles[:-1])
        reversal = (prev.close < prev.open and last.close > last.open) or (
            prev.close > prev.open and last.close < last.open
        )
        upper_wick = last.high - max(last.open, last.close)
        lower_wick = min(last.open, last.close) - last.low
        body = abs(last.close - last.open) or 1e-9
        wick_rejection = upper_wick > body * 1.5 or lower_wick > body * 1.5
        engulfing = (
            last.high >= prev.high
            and last.low <= prev.low
            and abs(last.close - last.open) > abs(prev.close - prev.open)
        )
        score = 0.35
        score += 0.15 if trend in {"uptrend", "downtrend"} else 0.0
        score += 0.15 if breakout else 0.0
        score += 0.1 if reversal else 0.0
        score += 0.1 if wick_rejection else 0.0
        score += 0.1 if engulfing else 0.0
        score += 0.15 if volume_confirmed else 0.0
        return CandlePatternResult(
            trend=trend,
            breakout=breakout,
            reversal=reversal,
            wick_rejection=wick_rejection,
            engulfing=engulfing,
            volume_confirmed=volume_confirmed,
            confidence_score=round(min(score, 1.0), 4),
        )

    @staticmethod
    def _trend(closes: list[float]) -> str:
        if closes[-1] > closes[-2] > closes[-3]:
            return "uptrend"
        if closes[-1] < closes[-2] < closes[-3]:
            return "downtrend"
        return "range"

    @staticmethod
    def _direction(result: CandlePatternResult) -> DecisionAction:
        if result.reversal or result.wick_rejection:
            return DecisionAction.HOLD
        if result.trend == "uptrend" and (result.breakout or result.volume_confirmed):
            return DecisionAction.BUY
        if result.trend == "downtrend" and (result.breakout or result.volume_confirmed):
            return DecisionAction.SELL
        if result.trend == "uptrend" and result.confidence_score >= 0.5:
            return DecisionAction.BUY
        if result.trend == "downtrend" and result.confidence_score >= 0.5:
            return DecisionAction.SELL
        return DecisionAction.SKIP

    @staticmethod
    def _missing(symbol: str, timeframe: Timeframe, field_name: str) -> IntelligenceSignal:
        return IntelligenceSignal(
            name="candle_intelligence",
            symbol=symbol.upper(),
            timeframe=timeframe,
            direction=DecisionAction.SKIP,
            confidence=0.0,
            missing_data=[field_name],
            reason="Missing candle data; no candle signal generated.",
        )
