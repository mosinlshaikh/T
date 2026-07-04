from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class RestApiRequest:
    method: str
    path: str
    params: dict[str, Any] = field(default_factory=dict)
    authenticated: bool = False


@dataclass
class RestApiConnector:
    """REST connector skeleton.

    This does not store secrets and does not sign private requests yet.
    Private/account endpoints must remain disabled until the audited live phase.
    """

    base_url: str = "https://api.binance.com"
    allow_private_requests: bool = False

    def build_public_request(
        self, path: str, params: dict[str, Any] | None = None
    ) -> RestApiRequest:
        return RestApiRequest(method="GET", path=path, params=params or {}, authenticated=False)

    def build_private_request(
        self, path: str, params: dict[str, Any] | None = None
    ) -> RestApiRequest:
        if not self.allow_private_requests:
            raise RuntimeError("Private REST requests are disabled in paper/sandbox mode.")
        return RestApiRequest(method="GET", path=path, params=params or {}, authenticated=True)
