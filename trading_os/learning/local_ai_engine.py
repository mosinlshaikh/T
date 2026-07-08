from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from trading_os.db.repository import TradingOSRepository

ACTIONS = ("BUY", "SELL", "HOLD", "SKIP")
STRATEGY_KEYS = (
    "candle",
    "order_book",
    "whale",
    "news",
    "market_structure",
    "volume",
    "risk",
)


@dataclass(frozen=True)
class LocalAIInsight:
    name: str
    status: str
    score: float | str = "unknown"
    reason: str = ""
    evidence_refs: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class LocalAISnapshot:
    status: str
    learning_mode: str
    auto_strategy_change: bool
    live_trading_impact: bool
    market_king_score: float | str
    action_distribution: dict[str, int]
    confidence_profile: dict[str, Any]
    strategy_scores: dict[str, Any]
    adaptive_recommendations: list[str]
    guardrails: list[str]
    insights: list[LocalAIInsight]
    reason: str


@dataclass
class LocalAIMarketKingEngine:
    """Offline, evidence-only learning engine.

    This is intentionally not an LLM wrapper and does not require OpenAI,
    Gemini, Binance private API, or any other AI key. It analyzes persisted
    paper-mode records and produces advisory scoring only.
    """

    repository: TradingOSRepository

    def snapshot(self, limit: int = 500) -> LocalAISnapshot:
        decisions = self.repository.list_ai_decisions(limit)
        journal = self.repository.list_trade_journal(limit)
        signals = self.repository.list_strategy_signals(limit)
        audit = self.repository.list_audit_events(limit)
        market = self.repository.list_market_intelligence_snapshots(limit)

        if not decisions and not journal and not signals and not market:
            return LocalAISnapshot(
                status="insufficient_data",
                learning_mode="paper_only_local_ai",
                auto_strategy_change=False,
                live_trading_impact=False,
                market_king_score="unknown",
                action_distribution={action: 0 for action in ACTIONS},
                confidence_profile={
                    "status": "unknown",
                    "reason": "No persisted decisions are available.",
                },
                strategy_scores={key: "unknown" for key in STRATEGY_KEYS},
                adaptive_recommendations=[
                    "Run more paper scans with public market data before trusting any score."
                ],
                guardrails=self.guardrails(),
                insights=[],
                reason="No evidence means no learning output.",
            )

        action_distribution = self._action_distribution(decisions)
        confidence_profile = self._confidence_profile(decisions)
        strategy_scores = self._strategy_scores(signals, decisions, audit)
        quality_score = self._quality_score(
            decisions=decisions,
            journal=journal,
            audit=audit,
            market=market,
            strategy_scores=strategy_scores,
        )

        return LocalAISnapshot(
            status="ok",
            learning_mode="paper_only_local_ai",
            auto_strategy_change=False,
            live_trading_impact=False,
            market_king_score=quality_score,
            action_distribution=action_distribution,
            confidence_profile=confidence_profile,
            strategy_scores=strategy_scores,
            adaptive_recommendations=self._recommendations(
                decisions=decisions,
                journal=journal,
                audit=audit,
                strategy_scores=strategy_scores,
            ),
            guardrails=self.guardrails(),
            insights=self._insights(decisions, journal, audit, market),
            reason=(
                "Local AI uses persisted evidence only. It does not change strategy rules "
                "automatically and has no live trading impact."
            ),
        )

    @staticmethod
    def guardrails() -> list[str]:
        return [
            "No Data = No Trade",
            "No Proof = No Decision",
            "Paper-only learning mode",
            "Auto strategy changes disabled",
            "Live trading impact disabled",
            "No guaranteed profit language",
            "No fake whale/news claims",
            "Risk and zero-hallucination gates stay active",
        ]

    def _action_distribution(self, decisions: list[dict[str, Any]]) -> dict[str, int]:
        counts = {action: 0 for action in ACTIONS}
        for decision in decisions:
            action = str(decision.get("action", "SKIP")).upper()
            if action in counts:
                counts[action] += 1
            else:
                counts["SKIP"] += 1
        return counts

    def _confidence_profile(self, decisions: list[dict[str, Any]]) -> dict[str, Any]:
        values = [float(item.get("confidence", 0.0) or 0.0) for item in decisions]
        if not values:
            return {"status": "unknown", "reason": "No confidence history."}
        high = [value for value in values if value >= 0.7]
        medium = [value for value in values if 0.45 <= value < 0.7]
        low = [value for value in values if value < 0.45]
        return {
            "status": "ok",
            "average": round(sum(values) / len(values), 4),
            "high_count": len(high),
            "medium_count": len(medium),
            "low_count": len(low),
            "sample_size": len(values),
        }

    def _strategy_scores(
        self,
        signals: list[dict[str, Any]],
        decisions: list[dict[str, Any]],
        audit: list[dict[str, Any]],
    ) -> dict[str, Any]:
        scores: dict[str, Any] = {}
        blocked_count = len(
            [
                item
                for item in audit
                if item.get("event_type") in {"risk_rejection", "blocked_hallucination"}
            ]
        )
        decision_count = max(1, len(decisions))
        for key in STRATEGY_KEYS:
            matched_signals = [
                item for item in signals if key in str(item.get("signal", "")).lower()
            ]
            evidence_hits = len(matched_signals)
            raw_score = min(100.0, evidence_hits / decision_count * 100.0)
            penalty = min(35.0, blocked_count / decision_count * 10.0)
            scores[key] = {
                "score": round(max(0.0, raw_score - penalty), 2),
                "evidence_count": evidence_hits,
                "status": "evidence_based" if evidence_hits else "needs_more_data",
            }
        return scores

    def _quality_score(
        self,
        decisions: list[dict[str, Any]],
        journal: list[dict[str, Any]],
        audit: list[dict[str, Any]],
        market: list[dict[str, Any]],
        strategy_scores: dict[str, Any],
    ) -> float:
        decision_count = len(decisions)
        if decision_count == 0:
            return 0.0

        confidence = self._confidence_profile(decisions)
        avg_confidence = float(confidence.get("average", 0.0) or 0.0)
        evidence_depth = min(25.0, len(market) / max(1, decision_count) * 25.0)
        strategy_depth = sum(
            1 for value in strategy_scores.values() if value.get("status") == "evidence_based"
        )
        strategy_score = strategy_depth / len(STRATEGY_KEYS) * 25.0
        pnl_values = [float(item.get("realized_pnl", 0.0) or 0.0) for item in journal]
        outcome_score = 20.0 if pnl_values else 8.0
        safety_penalty = min(
            25.0,
            len(
                [
                    item
                    for item in audit
                    if item.get("event_type") in {"risk_rejection", "blocked_hallucination"}
                ]
            )
            / max(1, decision_count)
            * 15.0,
        )
        score = avg_confidence * 30.0 + evidence_depth + strategy_score + outcome_score
        return round(max(0.0, min(100.0, score - safety_penalty)), 2)

    def _recommendations(
        self,
        decisions: list[dict[str, Any]],
        journal: list[dict[str, Any]],
        audit: list[dict[str, Any]],
        strategy_scores: dict[str, Any],
    ) -> list[str]:
        recommendations: list[str] = []
        if len(decisions) < 50:
            recommendations.append("Collect at least 50 paper decisions before raising confidence.")
        if not journal:
            recommendations.append("Open/close more paper trades before judging outcome quality.")
        weak = [
            name
            for name, value in strategy_scores.items()
            if value.get("status") == "needs_more_data"
        ]
        if weak:
            recommendations.append(
                "Need more evidence for strategies: " + ", ".join(sorted(weak)) + "."
            )
        if any(item.get("event_type") == "blocked_hallucination" for item in audit):
            recommendations.append(
                "Keep zero-hallucination gate strict; it has blocked unsupported claims."
            )
        if not recommendations:
            recommendations.append(
                "Continue paper-only monitoring; no automatic strategy change recommended."
            )
        return recommendations

    def _insights(
        self,
        decisions: list[dict[str, Any]],
        journal: list[dict[str, Any]],
        audit: list[dict[str, Any]],
        market: list[dict[str, Any]],
    ) -> list[LocalAIInsight]:
        insights: list[LocalAIInsight] = []
        hold_skip = len(
            [item for item in decisions if str(item.get("action", "")).upper() in {"HOLD", "SKIP"}]
        )
        if decisions:
            insights.append(
                LocalAIInsight(
                    name="decision_discipline",
                    status="ok",
                    score=round(hold_skip / len(decisions) * 100.0, 2),
                    reason="Higher HOLD/SKIP ratio means the bot is refusing weak setups.",
                )
            )
        if journal:
            pnl_values = [float(item.get("realized_pnl", 0.0) or 0.0) for item in journal]
            insights.append(
                LocalAIInsight(
                    name="paper_outcome_memory",
                    status="ok",
                    score=round(sum(pnl_values), 8),
                    reason="Aggregate paper realized PnL only; not a prediction.",
                )
            )
        if audit:
            blocked = [
                item
                for item in audit
                if item.get("event_type") in {"risk_rejection", "blocked_hallucination"}
            ]
            insights.append(
                LocalAIInsight(
                    name="safety_blocks",
                    status="ok" if blocked else "quiet",
                    score=len(blocked),
                    reason="Counts persisted risk and hallucination blocks.",
                )
            )
        if market:
            insights.append(
                LocalAIInsight(
                    name="market_memory_depth",
                    status="ok",
                    score=len(market),
                    reason="Counts persisted market intelligence snapshots.",
                )
            )
        return insights
