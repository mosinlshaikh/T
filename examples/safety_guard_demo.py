from __future__ import annotations

from quality.hallucination_guard import (
    detect_unsafe_claims,
    enforce_research_output,
    sanitize_research_text,
)


def main() -> None:
    samples = [
        "This is a research observation about market volatility.",
        "This is guaranteed profit and 100% accurate.",
        "BUY Now because price will go up.",
        "This backtest shows historical behavior that needs human review.",
    ]

    for index, sample in enumerate(samples, start=1):
        print("=" * 60)
        print(f"Sample {index}")
        print("-" * 60)
        print("Original:")
        print(sample)

        blocked = detect_unsafe_claims(sample)
        result = sanitize_research_text(sample)
        enforced = enforce_research_output(sample)

        print("\nBlocked phrases:")
        print(blocked)

        print("\nSafe:")
        print(result.safe)

        print("\nSanitized:")
        print(result.sanitized_text)

        print("\nEnforced output:")
        print(enforced)

    print("=" * 60)
    print("Research only. Not financial advice.")


if __name__ == "__main__":
    main()
