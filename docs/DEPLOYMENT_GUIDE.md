\# T Deployment Guide



\*\*Project:\*\* T

\*\*Maintainer:\*\* T Technology Research Lab

\*\*Status:\*\* Public Alpha / Research Software



```text

Research only. Not financial advice.

```



\## 1. Purpose



This guide explains basic deployment options for T.



T can be used locally for research, testing, backtesting, dashboard analytics, and demonstrations. Deployment support should be treated as technical setup guidance, not as managed financial operation.



\## 2. Deployment Status



T is currently public alpha research software.



Recommended use:



\* Local research setup

\* Developer demo

\* Backtest review

\* Dashboard walkthrough

\* Internal research environment

\* Prototype deployment



Not recommended as:



\* Live trading production system

\* Managed financial service

\* Broker execution system

\* Investment advisory platform

\* High-availability production finance system



\## 3. Local Setup



Clone the repository:



```bash

git clone https://github.com/mosin1982/T.git

cd T

```



Create a virtual environment:



```bash

python -m venv .venv

```



Activate the environment.



Windows PowerShell:



```powershell

.venv\\Scripts\\activate

```



Linux/macOS:



```bash

source .venv/bin/activate

```



Install dependencies:



```bash

python -m pip install --upgrade pip

pip install -r requirements.txt

```



Run quality checks:



```bash

python -m pytest -q

```



Run the dashboard:



```bash

python -m streamlit run dashboard/app.py

```



\## 4. Dashboard Deployment



The Streamlit dashboard is located at:



```text

dashboard/app.py

```



For local use:



```bash

python -m streamlit run dashboard/app.py

```



For server use, run from the project root and expose only the required port according to your environment policy.



Example:



```bash

python -m streamlit run dashboard/app.py --server.port 8501

```



\## 5. VPS / Server Guidance



A basic VPS deployment may include:



\* Ubuntu server

\* Python installed

\* Git installed

\* Virtual environment

\* Firewall configured

\* Streamlit dashboard process

\* Basic log monitoring

\* Optional reverse proxy



Basic steps:



```bash

sudo apt update

sudo apt install -y python3 python3-venv python3-pip git

git clone https://github.com/mosin1982/T.git

cd T

python3 -m venv .venv

source .venv/bin/activate

pip install -r requirements.txt

python -m pytest -q

python -m streamlit run dashboard/app.py --server.port 8501

```



\## 6. Docker Guidance



If Docker support is available in the repository, a typical flow may be:



```bash

docker build -t t-research-os .

docker run --rm -p 8501:8501 t-research-os

```



If Docker files are not configured for a given branch, use local Python deployment instead.



\## 7. Environment Variables



Future deployments may use environment variables for:



\* Data provider configuration

\* Dashboard settings

\* API keys

\* Report paths

\* Logging configuration



Never commit secrets to GitHub.



Do not store:



\* API keys

\* Passwords

\* OTPs

\* Wallet seed phrases

\* Private keys

\* Broker credentials

\* Recovery codes



\## 8. Deployment Checklist



Before sharing a deployment with users:



\* Run tests

\* Confirm dashboard starts

\* Confirm README is current

\* Confirm disclaimer is visible

\* Confirm safety docs are present

\* Confirm no secrets are committed

\* Confirm data source status

\* Confirm support scope

\* Confirm user understands research-only positioning



\## 9. Basic Troubleshooting



\### Dashboard does not start



Check:



```bash

python --version

pip install -r requirements.txt

python -m streamlit run dashboard/app.py

```



\### Tests fail



Run:



```bash

python -m pytest -q

```



Review the first failure and fix before deployment.



\### Port already in use



Try another port:



```bash

python -m streamlit run dashboard/app.py --server.port 8502

```



\### Missing dependency



Install dependencies again:



```bash

pip install -r requirements.txt

```



\## 10. Support Boundary



Deployment guidance does not include:



\* Financial advice

\* Investment advice

\* Trade recommendations

\* Legal compliance guarantee

\* Tax advice

\* Broker account operation

\* Managed trading

\* 24/7 production SLA unless separately agreed in writing



\## 11. User Responsibility



Users are responsible for:



\* Their own server

\* Their own credentials

\* Their own data

\* Their own legal compliance

\* Their own security policies

\* Their own financial decisions

\* Reviewing all system output before use



\## 12. Official Disclaimer



```text

T is research-only software.

It does not provide financial advice.

It does not provide investment advice.

It does not provide trade recommendations.

Deployment support is technical guidance only.

```



━━━━━━━━━━━━━━━━━━━━

T

T Technology Research Lab

━━━━━━━━━━━━━━━━━━━━



