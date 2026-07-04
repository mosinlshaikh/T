from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SymbolRules:
    symbol: str
    min_order_size: float
    tick_size: float
    lot_size: float
    step_size: float
    price_precision: int
    quantity_precision: int
    min_notional: float
    trading_active: bool = True
