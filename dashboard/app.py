from __future__ import annotations

import json
from pathlib import Path

import streamlit as st


st.set_page_config(
    page_title="T Mission Dashboard",
    page_icon="📊",
    layout="wide",
)

st.title("T Mission Dashboard")
st.caption("T Technology Research Lab — Financial Intelligence Operating System")

st.warning("Research only. Not financial advice.")

st.markdown(
    """
    ### System Overview

    T is an open-source Financial Intelligence Operating System for:

    - Market research
    - Paper trading
    - Backtesting
    - Risk analysis
    - Smart money intelligence
    """
)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("System", "T")

with col2:
    st.metric("Mode", "Research Only")

with col3:
    st.metric("Release", "v0.8.2-alpha")

with col4:
    st.metric("Status", "Alpha")


st.divider()

st.subheader("Mission Control")

checks = {
    "Repo files": Path("README.md").exists(),
    "Sample data": Path("data").exists(),
    "Tests folder": Path("tests").exists(),
    "Docs folder": Path("docs").exists(),
    "Backtest report": Path("reports/backtests/backtest_report.json").exists(),
}

for name, ok in checks.items():
    if ok:
        st.success(f"{name}: OK")
    else:
        st.error(f"{name}: Missing")


st.divider()

st.subheader("Backtest Report")

report_path = Path("reports/backtests/backtest_report.json")

if report_path.exists():
    try:
        report = json.loads(report_path.read_text(encoding="utf-8"))

        summary_cols = st.columns(4)

        with summary_cols[0]:
            st.metric("Starting Balance", report.get("starting_balance", "N/A"))

        with summary_cols[1]:
            st.metric("Ending Balance", report.get("ending_balance", "N/A"))

        with summary_cols[2]:
            st.metric("Net PnL", report.get("net_pnl", "N/A"))

        with summary_cols[3]:
            st.metric("Max Drawdown", report.get("max_drawdown_pct", "N/A"))

        st.json(report)

    except Exception as exc:
        st.error(f"Could not load backtest report: {exc}")
else:
    st.info(
        "No backtest report found yet. Run this command first: "
        "`python t_cli.py backtest`"
    )


st.divider()

st.subheader("Next Alpha Roadmap")

st.markdown(
    """
    - Streamlit dashboard
    - Backtest charts
    - Real-world observation mode UI
    - Strategy comparison
    - README screenshots
    - v0.9.0-alpha release
    """
)

st.caption("━━━━━━━━━━━━━━━━━━━━")
st.caption("T")
st.caption("T Technology Research Lab")
st.caption("━━━━━━━━━━━━━━━━━━━━")