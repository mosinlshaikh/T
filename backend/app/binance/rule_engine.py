from __future__ import annotations

from dataclasses import dataclass, field

from backend.app.binance.symbol_rules import SymbolRules


@dataclass
class BinanceRuleEngine:
    rules: dict[str, SymbolRules] = field(default_factory=dict)
    exchange_maintenance: bool = False

    def add_rules(self, rules: SymbolRules) -> None:
        self.rules[rules.symbol.upper()] = rules

    def get_rules(self, symbol: str) -> SymbolRules | None:
        return self.rules.get(symbol.upper())

    def validate_symbol_active(self, symbol: str) -> tuple[bool, str]:
        if self.exchange_maintenance:
            return False, "Exchange maintenance state."
        rules = self.get_rules(symbol)
        if rules is None:
            return False, "Symbol rules missing."
        if not rules.trading_active:
            return False, "Trading pair is not active."
        return True, "Symbol active."
