from modes.scoring import Signal


def format_console_alert(signal: Signal) -> str:
    return f"""
==============================
T SMART MONEY INTELLIGENCE
==============================
Asset        : {signal.asset}
Direction    : {signal.direction}
Price        : {signal.price}
Z-Score      : {signal.z_score:.2f}
T Alpha      : {signal.alpha_score}/100
Risk         : {signal.risk_label}

Explanation:
{signal.explanation}

Powered by T Technology Research Lab
Research only. Not financial advice.
==============================
""".strip()


def format_telegram_alert(signal: Signal) -> str:
    return f"""
<b>T SMART MONEY INTELLIGENCE</b>

<b>Asset:</b> {signal.asset}
<b>Direction:</b> {signal.direction}
<b>Price:</b> {signal.price}
<b>Z-Score:</b> {signal.z_score:.2f}
<b>T Alpha:</b> {signal.alpha_score}/100
<b>Risk:</b> {signal.risk_label}

<b>Explanation:</b>
{signal.explanation}

====================
<b>T</b>
<b>T Technology Research Lab</b>
====================

<i>Research only. Not financial advice.</i>
""".strip()
