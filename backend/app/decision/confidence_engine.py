from __future__ import annotations


def confidence_from_inputs(inputs: list[dict[str, object]]) -> float:
    scores = [
        float(item.get("confidence", 0.0)) for item in inputs if item.get("confidence") is not None
    ]
    return round(sum(scores) / len(scores), 4) if scores else 0.0
