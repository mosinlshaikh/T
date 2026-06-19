\# T Global Language Support



\*\*Project:\*\* T

\*\*Maintainer:\*\* T Technology Research Lab

\*\*Status:\*\* Public Alpha / Research Software



```text

Research only. Not financial advice.

```



\## 1. Purpose



T is designed as an English-first global public alpha project with planned multilingual documentation and dashboard support.



GitHub is a global platform. Users, developers, researchers, students, and contributors may come from different countries and language backgrounds.



This document defines the global language direction for T.



\## 2. Primary Language



The primary project language is:



```text

English

```



English should remain the default language for:



\* README

\* GitHub repository documentation

\* Developer documentation

\* CI/CD documentation

\* Technical architecture

\* Release notes

\* Security documentation



This keeps the project accessible to global technical users.



\## 3. Community Language Support



T may support community-facing explanations in:



\* Hindi

\* Hinglish



This is useful for Indian users, early supporters, students, small teams, and local training or walkthrough sessions.



\## 4. Planned Global Languages



Future documentation and dashboard support may include:



\* Spanish

\* Arabic

\* French

\* Portuguese

\* Indonesian

\* German

\* Japanese

\* Turkish



These languages may help the project reach wider global users and contributors.



\## 5. Translation Priority



Recommended priority:



| Priority | Language         | Purpose                               |

| -------- | ---------------- | ------------------------------------- |

| 1        | English          | Primary global technical language     |

| 2        | Hindi / Hinglish | Community support and Indian audience |

| 3        | Spanish          | Latin America and Spain               |

| 4        | Arabic           | Middle East and North Africa          |

| 5        | French           | Europe and Africa                     |

| 6        | Portuguese       | Brazil and Portugal                   |

| 7        | Indonesian       | Southeast Asia                        |



\## 6. What Should Be Translated First



Translate short, high-value documents first:



\* Project overview

\* Research-only disclaimer

\* Donation/support notice

\* Safety summary

\* Dashboard labels

\* Setup quickstart

\* Support scope summary



Do not translate complex legal or compliance statements casually. They should remain simple, conservative, and safety-reviewed.



\## 7. Dashboard Language Support



Future dashboard language selector may support:



```text

English

Hindi

Hinglish

Spanish

Arabic

French

Portuguese

```



Dashboard translations should cover:



\* Dashboard title

\* Research-only warning

\* Mission control labels

\* Backtest analytics labels

\* Safety panel text

\* Support links

\* Human review reminders



\## 8. Safety Translation Rule



The research-only disclaimer must be translated carefully.



Default disclaimer:



```text

Research only. Not financial advice.

```



Example translations may be maintained in a reviewed language file before being used in production-facing UI.



Unsafe translations, unclear financial language, or aggressive trading wording should not be used.



\## 9. Contribution Policy



Translation contributions may be accepted if they follow:



\* Clear language

\* Simple wording

\* Safety-first positioning

\* No trading instruction wording

\* No return assurance wording

\* No investment-advice wording

\* Human review before merge



\## 10. Recommended File Structure



Future translated docs may use:



```text

docs/i18n/

├─ README.hi.md

├─ README.es.md

├─ README.ar.md

├─ README.fr.md

├─ README.pt.md

└─ README.id.md

```



Future dashboard translations may use:



```text

i18n/

├─ \_\_init\_\_.py

└─ messages.py

```



\## 11. Official Position



```text

T is English-first today.

T may support multilingual documentation and dashboard labels over time.

All translations must preserve the research-only and safety-first positioning.

```



━━━━━━━━━━━━━━━━━━━━

T

T Technology Research Lab

━━━━━━━━━━━━━━━━━━━━



