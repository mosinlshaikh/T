from __future__ import annotations

from quality.hallucination_guard import sanitize_research_text


def main() -> None:
    sample_text = (
        "BTC will go up and this is a guaranteed profit setup. " "Buy now for a risk free return."
    )
    result = sanitize_research_text(sample_text)

    print("=" * 60)
    print("T Safety Guard Demo")
    print("=" * 60)
    print("Safe:", result.safe)
    print("Blocked phrases:", ", ".join(result.blocked_phrases))
    print("-" * 60)
    print(result.sanitized_text)
    print("=" * 60)
    print(result.disclaimer)


if __name__ == "__main__":
    main()
