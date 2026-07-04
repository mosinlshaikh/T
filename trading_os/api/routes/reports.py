from __future__ import annotations

from trading_os.analytics.safety_score import SafetyScoreEngine
from trading_os.api.dependencies import get_backend
from trading_os.api.framework import APIRouter
from trading_os.api.responses import ok
from trading_os.reports.generator import ReportGenerator

router = APIRouter(prefix="/reports", tags=["reports"])


def _generator() -> ReportGenerator:
    backend = get_backend()
    safety = SafetyScoreEngine(
        repository=backend.repository,
        config=backend.config,
        vault=backend.api_vault,
        emergency_state=backend.runtime_supervisor.state.value,
    )
    return ReportGenerator(
        repository=backend.repository,
        portfolio=backend.portfolio,
        safety_score_engine=safety,
    )


@router.get("/daily")
def daily_report() -> dict[str, object]:
    return ok(_generator().daily_report(), "Daily paper report loaded.")


@router.get("/weekly")
def weekly_report() -> dict[str, object]:
    return ok(_generator().weekly_report(), "Weekly paper report loaded.")


@router.get("/monthly")
def monthly_report() -> dict[str, object]:
    return ok(_generator().monthly_report(), "Monthly paper report loaded.")


@router.get("/performance")
def performance_report() -> dict[str, object]:
    return ok(_generator().latest_performance_snapshot(), "Performance report loaded.")


@router.get("/risk")
def risk_report() -> dict[str, object]:
    return ok(_generator().risk_report(), "Risk report loaded.")


@router.get("/hallucination")
def hallucination_report() -> dict[str, object]:
    return ok(_generator().hallucination_safety_report(), "Hallucination safety report loaded.")


@router.get("/skipped-trades")
def skipped_trade_report() -> dict[str, object]:
    return ok(_generator().skipped_trade_report(), "Skipped trade report loaded.")


@router.get("/strategies")
def strategy_report() -> dict[str, object]:
    return ok(_generator().strategy_comparison_report(), "Strategy report loaded.")


@router.get("/runtime")
def runtime_report() -> dict[str, object]:
    return ok(_generator().shutdown_runtime_report(), "Runtime report loaded.")
