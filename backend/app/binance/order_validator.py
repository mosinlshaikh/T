from __future__ import annotations

from dataclasses import dataclass

from backend.app.binance.rule_engine import BinanceRuleEngine


@dataclass(frozen=True)
class OrderValidationResult:
    valid: bool
    reasons: list[str]


@dataclass
class OrderValidator:
    rule_engine: BinanceRuleEngine

    def validate(
        self, symbol: str, price: float, quantity: float, balance: float
    ) -> OrderValidationResult:
        reasons: list[str] = []
        active, reason = self.rule_engine.validate_symbol_active(symbol)
        if not active:
            reasons.append(reason)
            return OrderValidationResult(False, reasons)
        rules = self.rule_engine.get_rules(symbol)
        if rules is None:
            return OrderValidationResult(False, ["Symbol rules missing."])
        notional = price * quantity
        if quantity < rules.min_order_size:
            reasons.append("Below minimum order size.")
        if notional < rules.min_notional:
            reasons.append("Below minimum notional.")
        if notional > balance:
            reasons.append("Insufficient balance.")
        if price <= 0 or quantity <= 0:
            reasons.append("Price and quantity must be positive.")
        return OrderValidationResult(not reasons, reasons)
