from __future__ import annotations

from enum import Enum


class EmergencyMode(str, Enum):
    NONE = "NONE"
    KILL_SWITCH = "KILL_SWITCH"
    READ_ONLY = "READ_ONLY"
