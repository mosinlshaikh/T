from __future__ import annotations

from dataclasses import dataclass

BANNED_PHRASES = [
    "guaranteed profit",
    "sure shot",
    "100% accurate",
    "risk free",
    "buy now",
    "sell now",
    "financial advice",
    "investment advice",
    "guaranteed return",
    "no loss",
    "will go up",
    "will go down",
    "must buy",
    "must sell",
]


RESEARCH_DISCLAIMER = "Research only. Not financial advice."


@dataclass(frozen=True)
class GuardResult:
    safe: bool
    blocked_phrases: list[str]
    sanitized_text: str
    disclaimer: str = RESEARCH_DISCLAIMER


def detect_unsafe_claims(text: str) -> list[str]:
    normalized = text.lower()
    return [phrase for phrase in BANNED_PHRASES if phrase in normalized]


def sanitize_research_text(text: str) -> GuardResult:
    blocked = detect_unsafe_claims(text)

    sanitized = text
    for phrase in blocked:
        sanitized = sanitized.replace(phrase, "[blocked unsafe claim]")
        sanitized = sanitized.replace(phrase.title(), "[blocked unsafe claim]")
        sanitized = sanitized.replace(phrase.upper(), "[blocked unsafe claim]")

    if RESEARCH_DISCLAIMER.lower() not in sanitized.lower():
        sanitized = f"{sanitized}\n\n{RESEARCH_DISCLAIMER}"

    return GuardResult(
        safe=len(blocked) == 0,
        blocked_phrases=blocked,
        sanitized_text=sanitized,
    )


def enforce_research_output(text: str) -> str:
    result = sanitize_research_text(text)
    return result.sanitized_text
