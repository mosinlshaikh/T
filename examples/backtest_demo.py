from __future__ import annotations

from pathlib import Path

from backtest.engine import run_backtest


def main() -> None:
    csv_path = Path("data/sample/btc_demo.csv")

    if not csv_path.exists():
        raise FileNotFoundError("Sample CSV not found. Expected: data/sample/btc_demo.csv")

    result = run_backtest(str(csv_path))

    print("=" * 60)
    print("T Backtest Demo")
    print("=" * 60)
    print("Research only. Not financial advice.")
    print("-" * 60)

    print(f"Starting Balance: {result.starting_balance}")
    print(f"Ending Balance: {result.ending_balance}")
    print(f"Net PnL: {result.net_pnl}")
    print(f"Max Drawdown %: {result.max_drawdown_pct}")
    print(f"Win Rate %: {result.win_rate_pct}")
    print(f"Profit Factor: {result.profit_factor}")
    print(f"Total Trades: {result.total_trades}")
    print(f"Average Win: {result.average_win}")
    print(f"Average Loss: {result.average_loss}")
    print(f"Best Trade PnL: {result.best_trade_pnl}")
    print(f"Worst Trade PnL: {result.worst_trade_pnl}")
    print(f"Average Return %: {result.average_return_pct}")

    print("-" * 60)
    print("Equity Curve:")
    print(result.equity_curve)

    print("-" * 60)
    print("Trades:")
    if not result.trades:
        print("No trades generated for this sample.")
    else:
        for trade in result.trades:
            print(trade)

    print("=" * 60)
    print("Research only. Not financial advice.")


if __name__ == "__main__":
    main()
