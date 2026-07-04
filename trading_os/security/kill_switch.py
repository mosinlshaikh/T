from __future__ import annotations

from dataclasses import dataclass


@dataclass
class EmergencyKillSwitch:
    active: bool = False
    reason: str = ""

    def activate(self, reason: str) -> None:
        self.active = True
        self.reason = reason or "Emergency kill switch activated."

    def clear_for_paper_mode(self) -> None:
        self.active = False
        self.reason = ""

    def assert_not_active(self) -> None:
        if self.active:
            raise RuntimeError(f"Emergency kill switch active: {self.reason}")
