from __future__ import annotations


def volume_spike(current_volume: float, average_volume: float, ratio: float = 2.0) -> bool:
    return average_volume > 0 and current_volume >= average_volume * ratio
