from __future__ import annotations

from typing import (
    Any,
    Dict,
    Optional,
    TYPE_CHECKING
)

if TYPE_CHECKING:
    from .client import Client
    from .http import HTTPClient


class State:
    def __init__(
        self,
        *,
        client: Client,
        http: HTTPClient,
        data: Optional[Dict[str, Any]] = None
    ):
        self.client = client
        self.http = http

        self.data = data

    @classmethod
    def from_state(cls, state):
        s = cls(
            client = state.client,
            http = state.http,
            data = state.data
        )

        return s