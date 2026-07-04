from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from enum import Enum
from typing import Any


class TradingStatus(str, Enum):
    TRADING = "TRADING"
    HALT = "HALT"
    BREAK = "BREAK"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class SymbolRules:
    symbol: str
    status: TradingStatus = TradingStatus.UNKNOWN
    min_order_size: Decimal = Decimal("0")
    tick_size: Decimal = Decimal("0")
    lot_size: Decimal = Decimal("0")
    price_precision: int = 0
    quantity_precision: int = 0
    min_notional: Decimal = Decimal("0")

    def is_trading(self) -> bool:
        return self.status == TradingStatus.TRADING


@dataclass(frozen=True)
class OrderValidation:
    allowed: bool
    reasons: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class RateLimitPlan:
    endpoint: str
    request_weight: int
    limit_per_minute: int = 1200

    @property
    def safe_capacity_remaining(self) -> int:
        return max(self.limit_per_minute - self.request_weight, 0)


@dataclass
class BinanceSpotKnowledgeEngine:
    symbols: dict[str, SymbolRules] = field(default_factory=dict)
    default_limit_per_minute: int = 1200

    def load_symbol_rules(self, exchange_info: dict[str, Any]) -> None:
        for item in exchange_info.get("symbols", []):
            rules = self._parse_symbol_rules(item)
            self.symbols[rules.symbol] = rules

    def get_rules(self, symbol: str) -> SymbolRules | None:
        return self.symbols.get(symbol.upper())

    def validate_order(self, symbol: str, price: float, quantity: float) -> OrderValidation:
        rules = self.get_rules(symbol)
        if rules is None:
            return OrderValidation(False, [f"Missing symbol rules for {symbol.upper()}."])

        reasons: list[str] = []
        price_d = self._decimal(price)
        qty_d = self._decimal(quantity)

        if not rules.is_trading():
            reasons.append(f"{rules.symbol} status is {rules.status.value}.")
        if qty_d < rules.min_order_size:
            reasons.append("Quantity below min order size.")
        if rules.lot_size and qty_d % rules.lot_size != 0:
            reasons.append("Quantity does not match lot size.")
        if rules.tick_size and price_d % rules.tick_size != 0:
            reasons.append("Price does not match tick size.")
        if price_d * qty_d < rules.min_notional:
            reasons.append("Order notional below minimum.")
        if self._decimal_places(price_d) > rules.price_precision:
            reasons.append("Price precision too high.")
        if self._decimal_places(qty_d) > rules.quantity_precision:
            reasons.append("Quantity precision too high.")

        return OrderValidation(not reasons, reasons)

    def rate_limit_plan(self, endpoint: str, request_weight: int) -> RateLimitPlan:
        return RateLimitPlan(
            endpoint=endpoint,
            request_weight=request_weight,
            limit_per_minute=self.default_limit_per_minute,
        )

    def _parse_symbol_rules(self, item: dict[str, Any]) -> SymbolRules:
        filters = {entry.get("filterType"): entry for entry in item.get("filters", [])}
        lot = filters.get("LOT_SIZE", {})
        price = filters.get("PRICE_FILTER", {})
        notional = filters.get("MIN_NOTIONAL", {}) or filters.get("NOTIONAL", {})

        return SymbolRules(
            symbol=str(item.get("symbol", "")).upper(),
            status=self._status(item.get("status", "UNKNOWN")),
            min_order_size=self._decimal(lot.get("minQty", "0")),
            tick_size=self._decimal(price.get("tickSize", "0")),
            lot_size=self._decimal(lot.get("stepSize", "0")),
            price_precision=int(item.get("pricePrecision", 0)),
            quantity_precision=int(item.get("quantityPrecision", 0)),
            min_notional=self._decimal(notional.get("minNotional", "0")),
        )

    @staticmethod
    def _decimal(value: object) -> Decimal:
        try:
            return Decimal(str(value))
        except (InvalidOperation, ValueError):
            return Decimal("0")

    @staticmethod
    def _status(value: object) -> TradingStatus:
        try:
            return TradingStatus(str(value))
        except ValueError:
            return TradingStatus.UNKNOWN

    @staticmethod
    def _decimal_places(value: Decimal) -> int:
        exponent = value.normalize().as_tuple().exponent
        return abs(exponent) if exponent < 0 else 0
