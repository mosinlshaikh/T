import json
from dataclasses import asdict
from pathlib import Path

from backtest.engine import BacktestResult


def result_to_dict(result: BacktestResult) -> dict:
    data = asdict(result)
    if data["profit_factor"] == float("inf"):
        data["profit_factor"] = "inf"
    return data


def save_backtest_report(
    result: BacktestResult, path: str = "reports/backtests/backtest_report.json"
) -> str:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result_to_dict(result), indent=2), encoding="utf-8")
    return str(out)


def format_backtest_summary(result: BacktestResult) -> str:
    return f"""
==============================
T BACKTEST REPORT
==============================
Starting Balance : {result.starting_balance}
Ending Balance   : {result.ending_balance}
Net PnL          : {result.net_pnl}
Trades           : {result.total_trades}
Win Rate         : {result.win_rate_pct}%
Profit Factor    : {result.profit_factor}
Max Drawdown     : {result.max_drawdown_pct}%
Average Win      : {result.average_win}
Average Loss     : {result.average_loss}
Best Trade PnL   : {result.best_trade_pnl}
Worst Trade PnL  : {result.worst_trade_pnl}
Avg Return       : {result.average_return_pct}%
Gross Profit     : {result.gross_profit}
Gross Loss       : {result.gross_loss}
Expectancy       : {result.expectancy}
Payoff Ratio     : {result.payoff_ratio}
Risk Per Trade   : {result.config.risk_pct}%
Rows Evaluated   : {result.diagnostics.evaluated_bars}
Qualified Signals: {result.diagnostics.qualified_signals}

Research only. Not financial advice.
==============================
""".strip()
