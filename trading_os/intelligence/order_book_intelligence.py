from __future__ import annotations

from dataclasses import dataclass

from trading_os.ai.decision_types import DecisionAction, EvidenceItem, EvidenceType
from trading_os.intelligence.types import IntelligenceSignal
from trading_os.market.order_book_engine import OrderBookSnapshot
from trading_os.market.timeframes import Timeframe, normalize_timeframe


@dataclass(frozen=True)
class OrderBookAnalysis:
    buy_wall: bool
    sell_wall: bool
    bid_ask_imbalance: float
    liquidity_gap: bool
    spread_risk: bool
    fake_wall_suspicion: bool
    confidence_score: float


@dataclass
class OrderBookIntelligenceEngine:
    wall_multiplier: float = 3.0
    spread_risk_pct: float = 0.2

    def analyze(
        self,
        symbol: str,
        timeframe: str | Timeframe,
        snapshot: OrderBookSnapshot | None,
    ) -> IntelligenceSignal:
        tf = normalize_timeframe(timeframe)
        if snapshot is None:
            return self._missing(symbol, tf, "order_book")
        if not snapshot.bids or not snapshot.asks:
            return self._missing(symbol, tf, "order_book_depth")

        analysis = self._analyze(snapshot)
        direction = DecisionAction.HOLD
        if analysis.buy_wall and not analysis.sell_wall and not analysis.spread_risk:
            direction = DecisionAction.BUY
        elif analysis.sell_wall and not analysis.buy_wall and not analysis.spread_risk:
            direction = DecisionAction.SELL

        evidence = [
            EvidenceItem(
                evidence_type=EvidenceType.ORDER_BOOK,
                source=snapshot.source,
                summary=(
                    f"buy_wall={analysis.buy_wall}; sell_wall={analysis.sell_wall}; "
                    f"imbalance={analysis.bid_ask_imbalance}; liquidity_gap={analysis.liquidity_gap}; "
                    f"spread_risk={analysis.spread_risk}; fake_wall_suspicion={analysis.fake_wall_suspicion}"
                ),
                confidence=analysis.confidence_score,
                payload={
                    "buy_wall": analysis.buy_wall,
                    "sell_wall": analysis.sell_wall,
                    "bid_ask_imbalance": analysis.bid_ask_imbalance,
                    "liquidity_gap": analysis.liquidity_gap,
                    "spread_risk": analysis.spread_risk,
                    "fake_wall_suspicion": analysis.fake_wall_suspicion,
                },
            )
        ]
        return IntelligenceSignal(
            name="order_book_intelligence",
            symbol=symbol.upper(),
            timeframe=tf,
            direction=direction,
            confidence=analysis.confidence_score,
            evidence=evidence,
            reason="Order book analysis completed with evidence.",
            risk_score=0.5 if analysis.spread_risk or analysis.fake_wall_suspicion else 0.0,
        )

    def _analyze(self, snapshot: OrderBookSnapshot) -> OrderBookAnalysis:
        bid_quantities = [level.quantity for level in snapshot.bids]
        ask_quantities = [level.quantity for level in snapshot.asks]
        avg_bid = sum(bid_quantities) / len(bid_quantities)
        avg_ask = sum(ask_quantities) / len(ask_quantities)
        max_bid = max(bid_quantities)
        max_ask = max(ask_quantities)
        bid_total = sum(bid_quantities)
        ask_total = sum(ask_quantities)
        imbalance = (bid_total - ask_total) / max(bid_total + ask_total, 1e-9)
        best_bid = max(level.price for level in snapshot.bids)
        best_ask = min(level.price for level in snapshot.asks)
        spread_pct = (best_ask - best_bid) / max(best_bid, 1e-9) * 100
        buy_wall = max_bid >= avg_bid * self.wall_multiplier
        sell_wall = max_ask >= avg_ask * self.wall_multiplier
        fake_wall = (buy_wall and bid_total < ask_total * 0.75) or (
            sell_wall and ask_total < bid_total * 0.75
        )
        liquidity_gap = spread_pct > self.spread_risk_pct * 0.5
        spread_risk = spread_pct > self.spread_risk_pct
        confidence = 0.45 + min(abs(imbalance), 0.35)
        confidence += 0.1 if buy_wall or sell_wall else 0.0
        confidence -= 0.2 if fake_wall or spread_risk else 0.0
        return OrderBookAnalysis(
            buy_wall=buy_wall,
            sell_wall=sell_wall,
            bid_ask_imbalance=round(imbalance, 4),
            liquidity_gap=liquidity_gap,
            spread_risk=spread_risk,
            fake_wall_suspicion=fake_wall,
            confidence_score=round(max(min(confidence, 1.0), 0.0), 4),
        )

    @staticmethod
    def _missing(symbol: str, timeframe: Timeframe, field_name: str) -> IntelligenceSignal:
        return IntelligenceSignal(
            name="order_book_intelligence",
            symbol=symbol.upper(),
            timeframe=timeframe,
            direction=DecisionAction.SKIP,
            confidence=0.0,
            missing_data=[field_name],
            reason="Missing order book data; no order book signal generated.",
        )
