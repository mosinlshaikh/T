from __future__ import annotations

from dataclasses import asdict

from trading_os.api.dependencies import get_backend
from trading_os.api.framework import APIRouter
from trading_os.api.responses import ok
from trading_os.learning.local_ai_engine import LocalAIMarketKingEngine

router = APIRouter(prefix="/learning", tags=["learning"])


def _engine() -> LocalAIMarketKingEngine:
    return LocalAIMarketKingEngine(repository=get_backend().repository)


@router.get("/local-ai")
def local_ai_snapshot() -> dict[str, object]:
    return ok(
        asdict(_engine().snapshot()),
        "Local paper-only AI learning snapshot loaded.",
        warnings=[
            "No external AI key is used.",
            "Advisory only; live trading remains disabled.",
        ],
    )


@router.get("/market-king-score")
def market_king_score() -> dict[str, object]:
    snapshot = _engine().snapshot()
    return ok(
        {
            "score": snapshot.market_king_score,
            "status": snapshot.status,
            "learning_mode": snapshot.learning_mode,
            "auto_strategy_change": snapshot.auto_strategy_change,
            "live_trading_impact": snapshot.live_trading_impact,
            "reason": snapshot.reason,
            "guardrails": snapshot.guardrails,
        },
        "Local AI market score loaded.",
    )


@router.get("/recommendations")
def learning_recommendations() -> dict[str, object]:
    snapshot = _engine().snapshot()
    return ok(
        {
            "recommendations": snapshot.adaptive_recommendations,
            "strategy_scores": snapshot.strategy_scores,
            "confidence_profile": snapshot.confidence_profile,
            "guardrails": snapshot.guardrails,
        },
        "Local AI recommendations loaded.",
    )
