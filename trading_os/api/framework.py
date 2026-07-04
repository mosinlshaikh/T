from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import Any, Callable

try:
    from fastapi import APIRouter, FastAPI, Request
    from fastapi.responses import JSONResponse
except ImportError:

    class Request:  # type: ignore[no-redef]
        pass

    class JSONResponse(dict):  # type: ignore[no-redef]
        def __init__(self, status_code: int, content: dict[str, Any]) -> None:
            super().__init__(content)
            self.status_code = status_code
            self.content = content

    class APIRouter:  # type: ignore[no-redef]
        def __init__(self, prefix: str = "", tags: list[str] | None = None) -> None:
            self.prefix = prefix
            self.tags = tags or []
            self.routes: list[tuple[str, str, Callable[..., Any]]] = []

        def get(self, path: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
            return self._route("GET", path)

        def post(self, path: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
            return self._route("POST", path)

        def put(self, path: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
            return self._route("PUT", path)

        def _route(
            self, method: str, path: str
        ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
            def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
                self.routes.append((method, path, func))
                return func

            return decorator

    class FastAPI:  # type: ignore[no-redef]
        def __init__(self, title: str, version: str) -> None:
            self.title = title
            self.version = version
            self.routers: list[APIRouter] = []
            self.exception_handlers: dict[type[Exception], Callable[..., Any]] = {}

        def include_router(self, router: APIRouter) -> None:
            self.routers.append(router)

        def exception_handler(
            self, exc_class: type[Exception]
        ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
            def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
                self.exception_handlers[exc_class] = func
                return func

            return decorator


def jsonable(value: Any) -> Any:
    if is_dataclass(value):
        return jsonable(asdict(value))
    if isinstance(value, dict):
        return {str(key): jsonable(item) for key, item in value.items()}
    if isinstance(value, list):
        return [jsonable(item) for item in value]
    if isinstance(value, tuple):
        return [jsonable(item) for item in value]
    if hasattr(value, "value"):
        return value.value
    return value
