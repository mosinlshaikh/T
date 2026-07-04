from __future__ import annotations


def execute_live_order(*_args: object, **_kwargs: object) -> None:
    raise RuntimeError("Live trading execution is disabled.")
