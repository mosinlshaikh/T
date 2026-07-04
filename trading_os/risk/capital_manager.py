from __future__ import annotations

from dataclasses import dataclass

from trading_os.ai.decision_types import EvidenceItem, EvidenceType


@dataclass(frozen=True)
class CapitalPlan:
    allowed: bool
    symbol: str
    balance: float
    allocation: float
    reason: str


@dataclass
class CapitalManager:
    default_allocation_pct: float = 1.0

    def plan_paper_allocation(self, symbol: str, balance: float) -> CapitalPlan:
        if balance <= 0:
            return CapitalPlan(False, symbol.upper(), balance, 0.0, "No capital available.")
        allocation = balance * (self.default_allocation_pct / 100)
        return CapitalPlan(
            True, symbol.upper(), balance, round(allocation, 2), "Paper allocation ready."
        )

    def to_evidence(self, plan: CapitalPlan) -> EvidenceItem:
        return EvidenceItem(
            evidence_type=EvidenceType.CAPITAL_CHECK,
            source="capital_manager",
            summary=plan.reason,
            confidence=1.0 if plan.allowed else 0.0,
            payload={"allocation": plan.allocation, "balance": plan.balance},
        )
