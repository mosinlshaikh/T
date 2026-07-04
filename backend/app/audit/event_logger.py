from __future__ import annotations


def event(name: str, details: dict[str, object]) -> dict[str, object]:
    return {"name": name, "details": details}
