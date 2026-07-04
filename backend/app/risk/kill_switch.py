from __future__ import annotations

from dataclasses import dataclass


@dataclass
class EmergencyKillSwitch:
    active: bool = False
    reason: str = ""

    def activate(self, reason: str) -> None:
        self.active = True
        self.reason = reason

    def assert_clear(self) -> None:
        if self.active:
            raise RuntimeError(f"Emergency kill switch active: {self.reason}")
