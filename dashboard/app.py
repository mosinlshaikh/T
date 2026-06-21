from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import streamlit as st

REPORT_PATH = Path("reports/backtests/backtest_report.json")
DISCLAIMER = "Research only. Not financial advice."


def load_backtest_report(path: Path = REPORT_PATH) -> tuple[dict[str, Any] | None, str | None]:
    if not path.exists():
        return None, f"Backtest report not found: {path}"

    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except (json.JSONDecodeError, OSError) as exc:
        return None, f"Could not load backtest report: {exc}"


def display_value(report: dict[str, Any], key: str, fallback: str = "N/A") -> Any:
    value = report.get(key, fallback)
    return fallback if value is None else value


def money(value: Any) -> str:
    if isinstance(value, int | float):
        return f"{value:,.2f}"
    return str(value)


def pct(value: Any) -> str:
    if isinstance(value, int | float):
        return f"{value:.2f}%"
    return str(value)


def pnl_state(value: Any) -> str:
    if not isinstance(value, int | float):
        return "Unknown"
    if value > 0:
        return "Positive"
    if value < 0:
        return "Negative"
    return "Flat"


def render_mission_control() -> None:
    checks = {
        "README": Path("README.md").exists(),
        "Sample data": Path("data/sample/btc_demo.csv").exists(),
        "Tests": Path("tests").exists(),
        "Docs": Path("docs").exists(),
        "Backtest report": REPORT_PATH.exists(),
    }

    st.subheader("Mission Control")
    check_cols = st.columns(len(checks))
    for col, (name, ok) in zip(check_cols, checks.items(), strict=False):
        with col:
            st.metric(name, "OK" if ok else "Missing")


def render_report_summary(report: dict[str, Any]) -> None:
    st.subheader("Backtest Analytics")
    top = st.columns(4)
    with top[0]:
        st.metric("Starting Balance", money(display_value(report, "starting_balance")))
    with top[1]:
        st.metric("Ending Balance", money(display_value(report, "ending_balance")))
    with top[2]:
        st.metric("Net PnL", money(display_value(report, "net_pnl")))
    with top[3]:
        st.metric("PnL State", pnl_state(report.get("net_pnl")))

    bottom = st.columns(4)
    with bottom[0]:
        st.metric("Trades", display_value(report, "total_trades", len(report.get("trades", []))))
    with bottom[1]:
        st.metric("Win Rate", pct(display_value(report, "win_rate_pct")))
    with bottom[2]:
        st.metric("Profit Factor", display_value(report, "profit_factor"))
    with bottom[3]:
        st.metric("Max Drawdown", pct(display_value(report, "max_drawdown_pct")))


def render_equity_curve(report: dict[str, Any]) -> None:
    equity_curve = report.get("equity_curve") or []
    st.subheader("Equity Curve")

    if len(equity_curve) < 2:
        st.info("Run a fresh backtest to generate a full equity curve.")
        return

    st.line_chart(equity_curve)


def render_risk_diagnostics(report: dict[str, Any]) -> None:
    config = report.get("config") or {}
    diagnostics = report.get("diagnostics") or {}

    st.subheader("Risk Diagnostics")
    risk_cols = st.columns(4)
    with risk_cols[0]:
        st.metric("Risk / Trade", pct(display_value(config, "risk_pct")))
    with risk_cols[1]:
        st.metric("Fee", f"{display_value(config, 'fee_bps')} bps")
    with risk_cols[2]:
        st.metric("Slippage", f"{display_value(config, 'slippage_bps')} bps")
    with risk_cols[3]:
        st.metric("Max Exposure", pct(display_value(diagnostics, "max_exposure_pct")))

    signal_cols = st.columns(4)
    with signal_cols[0]:
        st.metric("Data Rows", display_value(diagnostics, "data_rows"))
    with signal_cols[1]:
        st.metric("Evaluated Bars", display_value(diagnostics, "evaluated_bars"))
    with signal_cols[2]:
        st.metric("Qualified Signals", display_value(diagnostics, "qualified_signals"))
    with signal_cols[3]:
        st.metric("Warmup Bars", display_value(diagnostics, "warmup_bars"))

    pnl_cols = st.columns(4)
    with pnl_cols[0]:
        st.metric("Gross Profit", money(display_value(report, "gross_profit")))
    with pnl_cols[1]:
        st.metric("Gross Loss", money(display_value(report, "gross_loss")))
    with pnl_cols[2]:
        st.metric("Expectancy", money(display_value(report, "expectancy")))
    with pnl_cols[3]:
        st.metric("Payoff Ratio", display_value(report, "payoff_ratio"))


def render_trade_table(report: dict[str, Any]) -> None:
    trades = report.get("trades") or []
    st.subheader("Trade Table")

    if not trades:
        st.info("No trades are available in the current report.")
        return

    st.dataframe(
        trades,
        hide_index=True,
        use_container_width=True,
        column_order=[
            "asset",
            "side",
            "entry_price",
            "exit_price",
            "pnl",
            "return_pct",
            "alpha",
            "z",
        ],
    )


def render_safety_panel(report: dict[str, Any] | None) -> None:
    st.subheader("Research Safety")
    st.warning(DISCLAIMER)

    safety_checks = {
        "Research-only disclaimer": True,
        "No live-order execution in dashboard": True,
        "Human review required": True,
        "Backtest report loaded": report is not None,
    }

    for label, ok in safety_checks.items():
        st.write(f"{label}: {'OK' if ok else 'Missing'}")


st.set_page_config(
    page_title="T Mission Dashboard",
    page_icon="T",
    layout="wide",
)

st.title("T Mission Dashboard")
st.caption("T Technology Research Lab - Financial Intelligence Operating System")

overview_tab, analytics_tab, trades_tab, safety_tab = st.tabs(
    ["Overview", "Analytics", "Trades", "Safety"]
)

report, error = load_backtest_report()

with overview_tab:
    st.markdown("""
        ### System Overview

        T is a research-first framework for market analysis, paper trading,
        backtesting, risk review, and safety-oriented financial research output.
        """)

    status_cols = st.columns(4)
    with status_cols[0]:
        st.metric("System", "T")
    with status_cols[1]:
        st.metric("Mode", "Research Only")
    with status_cols[2]:
        st.metric("Target Release", "v0.10.0-alpha")
    with status_cols[3]:
        st.metric("Status", "Public Alpha")

    st.divider()
    render_mission_control()

with analytics_tab:
    if error:
        st.info(error)
        st.code("python t_cli.py backtest", language="bash")
    elif report:
        render_report_summary(report)
        st.divider()
        render_equity_curve(report)
        st.divider()
        render_risk_diagnostics(report)
        with st.expander("Raw report JSON"):
            st.json(report)

with trades_tab:
    if error:
        st.info(error)
    elif report:
        render_trade_table(report)

with safety_tab:
    render_safety_panel(report)
    st.divider()
    st.subheader("Next Alpha Priorities")
    st.markdown("""
        - Strategy comparison
        - Report history selection
        - Data quality diagnostics
        - Risk exposure review
        - Dashboard deployment profile
        """)

st.caption("T")
st.caption("T Technology Research Lab")
