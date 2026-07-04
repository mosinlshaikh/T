from __future__ import annotations

from enum import Enum


class BotMode(str, Enum):
    NORMAL = "NORMAL"
    CAUTION = "CAUTION"
    PAUSE = "PAUSE"
    EMERGENCY_STOP = "EMERGENCY_STOP"
    READ_ONLY = "READ_ONLY"
