from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="T Mission Dashboard",
    page_icon="📊",
    layout="wide",
)

st.title("T Mission Dashboard")
st.caption("T Technology Research Lab — Financial Intelligence Operating System")

st.warning("Research only. Not financial advice.")

st.markdown("""
    ### System Overview

    T is an open-source Financial Intelligence Operating System for:

    - Market research
    - Paper trading
    - Backtesting
    - Risk analysis
    - Smart money intelligence
    - Hallucination-resistant research output
    """)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("System", "T")

with col2:
    st.metric("Mode", "Research Only")

with col3:
    st.metric("Target Release", "v0.10.0-alpha")

with col4:
    st.metric("Status", "Repo Update")

st.divider()

st.subheader("Mission Control")

checks = {
    "README": Path("README.md").exists(),
    "Sample data": Path("data").exists(),
    "Tests folder": Path("tests").exists(),
    "Docs folder": Path("docs").exists(),
    "Backtest module": Path("backtest/engine.py").exists(),
    "Backtest report": Path("reports/backtests/backtest_report.json").exists(),
    "Hallucination guard": Path("quality/hallucination_guard.py").exists(),
}

for name, ok in checks.items():
    if ok:
        st.success(f"{name}: OK")
    else:
        st.error(f"{name}: Missing")

st.divider()

st.subheader("Backtest Analytics")

report_path = Path("reports/backtests/backtest_report.json")

if report_path.exists():
    try:
        report = json.loads(report_path.read_text(encoding="utf-8"))

        metric_cols = st.columns(4)

        with metric_cols[0]:
            st.metric("Starting Balance", report.get("starting_balance", "N/A"))

        with metric_cols[1]:
            st.metric("Ending Balance", report.get("ending_balance", "N/A"))

        with metric_cols[2]:
            st.metric("Net PnL", report.get("net_pnl", "N/A"))

        with metric_cols[3]:
            st.metric("Max Drawdown %", report.get("max_drawdown_pct", "N/A"))

        metric_cols_2 = st.columns(4)

        with metric_cols_2[0]:
            st.metric("Total Trades", report.get("total_trades", "N/A"))

        with metric_cols_2[1]:
            st.metric("Win Rate %", report.get("win_rate_pct", "N/A"))

        with metric_cols_2[2]:
            st.metric("Profit Factor", report.get("profit_factor", "N/A"))

        with metric_cols_2[3]:
            st.metric("Average Return %", report.get("average_return_pct", "N/A"))

        metric_cols_3 = st.columns(4)

        with metric_cols_3[0]:
            st.metric("Average Win", report.get("average_win", "N/A"))

        with metric_cols_3[1]:
            st.metric("Average Loss", report.get("average_loss", "N/A"))

        with metric_cols_3[2]:
            st.metric("Best Trade PnL", report.get("best_trade_pnl", "N/A"))

        with metric_cols_3[3]:
            st.metric("Worst Trade PnL", report.get("worst_trade_pnl", "N/A"))

        equity_curve = report.get("equity_curve", [])

        if isinstance(equity_curve, list) and equity_curve:
            st.subheader("Equity Curve")
            equity_df = pd.DataFrame(
                {
                    "step": list(range(len(equity_curve))),
                    "equity": equity_curve,
                }
            )
            st.line_chart(equity_df, x="step", y="equity")
        else:
            st.info("No equity curve found in the backtest report yet.")

        trades = report.get("trades", [])

        if isinstance(trades, list) and trades:
            st.subheader("Trade Table")
            trades_df = pd.DataFrame(trades)
            st.dataframe(trades_df, use_container_width=True)
        else:
            st.info("No trades found in the backtest report yet.")

        with st.expander("Raw Backtest JSON"):
            st.json(report)

    except (json.JSONDecodeError, OSError) as exc:
        st.error(f"Could not load backtest report: {exc}")
else:
    st.info("No backtest report found yet. Run this command first: " "`python t_cli.py backtest`")

st.divider()

st.subheader("Research Safety Panel")

st.markdown("""
    T is designed for research-only financial intelligence.

    Current safety direction:

    - No guaranteed-profit language
    - No buy/sell advice
    - No investment advice
    - No risk-free claims
    - Evidence-first research output
    - Hallucination-resistant output guard
    """)

st.warning("Research only. Not financial advice.")

st.divider()

st.subheader("Next Repo Updates Before v0.10.0-alpha")

st.markdown("""
    - Dashboard analytics visualization
    - Hallucination guard integration
    - Safety policy documentation
    - Services/pricing documentation
    - README final polish
    - Full QA before release
    """)

st.caption("━━━━━━━━━━━━━━━━━━━━")
st.caption("T")
st.caption("T Technology Research Lab")
st.caption("━━━━━━━━━━━━━━━━━━━━")
