from backtest.engine import BacktestConfig, BacktestDiagnostics, BacktestResult, BacktestTrade
from backtest.report import format_backtest_summary, result_to_dict


def sample_result() -> BacktestResult:
    return BacktestResult(
        trades=[
            BacktestTrade(
                asset="BTC/USDT",
                entry_price=100.0,
                exit_price=105.0,
                side="LONG",
                pnl=5.0,
                return_pct=0.05,
                alpha=80.0,
                z=3.0,
            )
        ],
        starting_balance=10000.0,
        ending_balance=10005.0,
        max_drawdown_pct=0.0,
        win_rate_pct=100.0,
        profit_factor=float("inf"),
        net_pnl=5.0,
        total_trades=1,
        average_win=5.0,
        average_loss=0.0,
        best_trade_pnl=5.0,
        worst_trade_pnl=5.0,
        average_return_pct=0.05,
        equity_curve=[10000.0, 10005.0],
        gross_profit=5.0,
        gross_loss=0.0,
        expectancy=5.0,
        payoff_ratio=0.0,
        config=BacktestConfig(csv_path="sample.csv", risk_pct=1.0, hold_bars=2),
        diagnostics=BacktestDiagnostics(
            data_rows=10,
            evaluated_bars=6,
            warmup_bars=3,
            qualified_signals=1,
            max_position_size=100.0,
            average_position_size=100.0,
            max_exposure_pct=1.0,
        ),
    )


def test_result_to_dict_serializes_infinite_profit_factor():
    data = result_to_dict(sample_result())

    assert data["profit_factor"] == "inf"
    assert data["equity_curve"] == [10000.0, 10005.0]
    assert data["config"]["risk_pct"] == 1.0
    assert data["diagnostics"]["qualified_signals"] == 1


def test_format_backtest_summary_is_windows_console_safe():
    summary = format_backtest_summary(sample_result())

    assert "Average Win" in summary
    assert "Risk Per Trade" in summary
    assert "Qualified Signals" in summary
    assert "Research only. Not financial advice." in summary
    assert all(ord(char) < 128 for char in summary)
