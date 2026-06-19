\# T Examples



This folder contains practical examples for using T as a research-only financial intelligence system.



```text

Research only. Not financial advice.

```



\## Available Examples



| Example           | Purpose                                          |

| ----------------- | ------------------------------------------------ |

| Backtest demo     | Run a sample backtest and review analytics       |

| Dashboard demo    | Launch the T Mission Dashboard                   |

| Safety guard demo | Test hallucination-resistant output guard        |

| Research workflow | Understand the recommended research-only process |



\## 1. Run Tests



From the project root:



```bash

python -m pytest -q

```



\## 2. Run Dashboard



```bash

python -m streamlit run dashboard/app.py

```



\## 3. Run Backtest



If the CLI is available:



```bash

python t\_cli.py backtest

```



\## 4. Safety Guard Example



The hallucination-resistant guard helps reduce unsafe financial language in research output.



Example purpose:



\* Detect unsafe financial claims

\* Sanitize unsafe text

\* Append research-only disclaimer

\* Keep output aligned with safety policy



\## 5. Research Workflow



Recommended workflow:



1\. Load sample/demo data

2\. Run scoring or backtest

3\. Review output metrics

4\. Review equity curve and trade table

5\. Check safety status

6\. Apply human review

7\. Do not treat output as financial advice



\## Disclaimer



T is research-only software. It does not provide financial advice, investment advice, trade recommendations, portfolio management, or profit assurance.



━━━━━━━━━━━━━━━━━━━━

T

T Technology Research Lab

━━━━━━━━━━━━━━━━━━━━



