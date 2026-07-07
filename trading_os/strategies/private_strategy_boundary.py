from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class StrategyPackVisibility(str, Enum):
    PUBLIC_INTERFACE = "PUBLIC_INTERFACE"
    PRIVATE_PRODUCTION_PACK = "PRIVATE_PRODUCTION_PACK"


@dataclass(frozen=True)
class PrivateStrategyBoundary:
    """Boundary for future private production strategy packs.

    Public code exposes interfaces and safe placeholders only. Proprietary
    scoring formulas should remain in private modules or server-side config.
    """

    visibility: StrategyPackVisibility = StrategyPackVisibility.PUBLIC_INTERFACE
    production_pack_loaded: bool = False
    note: str = "No proprietary whale/news/scoring formula is hardcoded in the public APK or repo."

    def assert_public_safe(self) -> None:
        if self.visibility == StrategyPackVisibility.PRIVATE_PRODUCTION_PACK:
            raise RuntimeError("Private production strategy pack must not be bundled publicly.")
