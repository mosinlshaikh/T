from __future__ import annotations

from dataclasses import dataclass
from statistics import mean

from trading_os.market.candle_engine import Candle
from trading_os.market.timeframes import Timeframe, normalize_timeframe


@dataclass(frozen=True)
class CandleStudy:
    symbol: str
    timeframe: Timeframe
    candle_count: int
    latest_close: float | None
    price_change_pct: float
    trend: str
    move_reason: str
    evidence: list[str]
    learning_notes: list[str]
    confidence_score: float
    missing_data: list[str]


class CandleStudyEngine:
    """Evidence-only candle study.

    This is not self-modifying AI. It records recurring candle explanations and
    produces advisory learning notes from observed candles only.
    """

    min_candles = 5

    def study(self, symbol: str, timeframe: str | Timeframe, candles: list[Candle]) -> CandleStudy:
        tf = normalize_timeframe(timeframe)
        relevant = [item for item in candles if item.symbol.upper() == symbol.upper()]
        if len(relevant) < self.min_candles:
            return CandleStudy(
                symbol=symbol.upper(),
                timeframe=tf,
                candle_count=len(relevant),
                latest_close=None,
                price_change_pct=0.0,
                trend="unknown",
                move_reason="Not enough candle evidence; No Data = No Trade.",
                evidence=[],
                learning_notes=["Collect more verified candles before learning a pattern."],
                confidence_score=0.0,
                missing_data=["candles"],
            )

        candles = relevant[-min(len(relevant), 120) :]
        first = candles[0]
        last = candles[-1]
        prev = candles[-2]
        closes = [item.close for item in candles]
        highs = [item.high for item in candles]
        lows = [item.low for item in candles]
        volumes = [item.volume for item in candles]
        previous_volumes = volumes[:-1] or [0.0]
        average_volume = mean(previous_volumes)
        price_change_pct = ((last.close - first.open) / first.open) * 100 if first.open else 0.0
        latest_change_pct = ((last.close - prev.close) / prev.close) * 100 if prev.close else 0.0
        body = abs(last.close - last.open)
        full_range = max(last.high - last.low, 1e-9)
        body_ratio = body / full_range
        upper_wick = last.high - max(last.open, last.close)
        lower_wick = min(last.open, last.close) - last.low
        volume_ratio = last.volume / average_volume if average_volume > 0 else 0.0
        resistance = max(highs[:-1])
        support = min(lows[:-1])
        breakout_up = last.close > resistance
        breakdown_down = last.close < support
        bullish_close = last.close > last.open
        bearish_close = last.close < last.open

        trend = self._trend(closes)
        reasons: list[str] = []
        evidence = [
            f"price_change_pct={round(price_change_pct, 4)}",
            f"latest_change_pct={round(latest_change_pct, 4)}",
            f"volume_ratio={round(volume_ratio, 4)}",
            f"body_ratio={round(body_ratio, 4)}",
            f"support={round(support, 8)}",
            f"resistance={round(resistance, 8)}",
        ]
        if breakout_up:
            reasons.append("price closed above recent resistance")
        if breakdown_down:
            reasons.append("price closed below recent support")
        if volume_ratio >= 1.25:
            reasons.append("latest volume is above recent average")
        if upper_wick > body * 1.5:
            reasons.append("upper wick shows selling pressure near the high")
        if lower_wick > body * 1.5:
            reasons.append("lower wick shows buying pressure near the low")
        if bullish_close and body_ratio >= 0.45:
            reasons.append("latest candle closed bullish with meaningful body")
        if bearish_close and body_ratio >= 0.45:
            reasons.append("latest candle closed bearish with meaningful body")
        if not reasons:
            reasons.append("price is moving inside recent range without strong confirmation")

        confidence = 0.35
        confidence += 0.15 if trend in {"uptrend", "downtrend"} else 0.0
        confidence += 0.15 if breakout_up or breakdown_down else 0.0
        confidence += 0.15 if volume_ratio >= 1.25 else 0.0
        confidence += 0.1 if upper_wick > body * 1.5 or lower_wick > body * 1.5 else 0.0
        confidence += 0.1 if body_ratio >= 0.45 else 0.0

        learning_notes = self._learning_notes(
            trend=trend,
            price_change_pct=price_change_pct,
            volume_ratio=volume_ratio,
            breakout_up=breakout_up,
            breakdown_down=breakdown_down,
            upper_wick=upper_wick,
            lower_wick=lower_wick,
            body=body,
        )
        direction = (
            "upar" if latest_change_pct > 0 else "niche" if latest_change_pct < 0 else "sideways"
        )
        return CandleStudy(
            symbol=symbol.upper(),
            timeframe=tf,
            candle_count=len(candles),
            latest_close=round(last.close, 8),
            price_change_pct=round(price_change_pct, 4),
            trend=trend,
            move_reason=f"Latest candle {direction} gaya because " + "; ".join(reasons) + ".",
            evidence=evidence,
            learning_notes=learning_notes,
            confidence_score=round(min(confidence, 1.0), 4),
            missing_data=[],
        )

    @staticmethod
    def _trend(closes: list[float]) -> str:
        if len(closes) < 5:
            return "unknown"
        short = mean(closes[-3:])
        long = mean(closes[-min(len(closes), 12) :])
        if short > long and closes[-1] > closes[-2]:
            return "uptrend"
        if short < long and closes[-1] < closes[-2]:
            return "downtrend"
        return "range"

    @staticmethod
    def _learning_notes(
        *,
        trend: str,
        price_change_pct: float,
        volume_ratio: float,
        breakout_up: bool,
        breakdown_down: bool,
        upper_wick: float,
        lower_wick: float,
        body: float,
    ) -> list[str]:
        notes: list[str] = []
        if abs(price_change_pct) < 0.15 and trend == "range":
            notes.append("Range market: wait for breakout plus volume confirmation.")
        if breakout_up and volume_ratio >= 1.25:
            notes.append(
                "Breakout with volume: mark as stronger bullish evidence, still require risk check."
            )
        if breakdown_down and volume_ratio >= 1.25:
            notes.append("Breakdown with volume: mark as stronger bearish/risk evidence.")
        if upper_wick > body * 1.5:
            notes.append("Repeated upper wicks near resistance should reduce BUY confidence.")
        if lower_wick > body * 1.5:
            notes.append("Repeated lower wicks near support should reduce SELL confidence.")
        if volume_ratio < 0.8:
            notes.append("Low volume move: avoid trusting candle direction alone.")
        if not notes:
            notes.append("Pattern is neutral; keep collecting outcomes before changing strategy.")
        notes.append(
            "Learning is advisory only; it does not auto-enable live trading or guarantee profit."
        )
        return notes
