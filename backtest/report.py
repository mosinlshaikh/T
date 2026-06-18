from dataclasses import asdict
from pathlib import Path
import json


from backtest.engine import BacktestResult

def result_to_dict(result: BacktestResult) -> dict:
    d = asdict(result)
    if d["profit_factor"] == float("inf"):
        d["profit_factor"] = "inf"
    return d

def save_backtest_report(result: BacktestResult, path: str = "reports/backtests/backtest_report.json") -> str:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result_to_dict(result), indent=2), encoding="utf-8")
    return str(out)

def format_backtest_summary(result: BacktestResult) -> str:
    return f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
T BACKTEST REPORT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Starting Balance : {result.starting_balance}
Ending Balance   : {result.ending_balance}
Net PnL          : {result.net_pnl}
Trades           : {len(result.trades)}
Win Rate         : {result.win_rate_pct}%
Profit Factor    : {result.profit_factor}
Max Drawdown     : {result.max_drawdown_pct}%

Research only. Not financial advice.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""".strip()
