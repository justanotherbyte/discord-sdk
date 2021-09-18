from __future__ import annotations

from typing import TYPE_CHECKING

from .http import Route

if TYPE_CHECKING:
    from .state import State

class Webhook:

    _state: State

    def __init__(
        self,
        endpoint: str,
        **kwargs
    ):
        self.endpoint = endpoint
        self.kwargs = kwargs

    def POST(self, **kwargs):
        route = Route("POST", self.endpoint, **self.kwargs)
        return self._state.http.request(route, **kwargs)

    def PATCH(self, **kwargs):
        route = Route("PATCH", self.endpoint, **self.kwargs)
        return self._state.http.request(route, **kwargs)

    def DELETE(self, **kwargs):
        route = Route("DELETE", self.endpoint, **self.kwargs)
        return self._state.http.request(route, **kwargs)

    def GET(self, **kwargs):
        route = Route("GET", self.endpoint, **self.kwargs)
        return self._state.http.request(route, **kwargs)