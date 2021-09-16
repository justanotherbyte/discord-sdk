from __future__ import annotations

import asyncio

from typing import (
    Optional,
    TYPE_CHECKING,
    Dict
)

import aiohttp

if TYPE_CHECKING:
    from aiohttp import (
        ClientSession,
        ClientWebSocketResponse
    )


class Route:
    BASE = "https://discord.com/api/v8"
    def __init__(self, method: str, endpoint: str, **params):
        self.method = method
        self.url = self.BASE + endpoint.format(**params)


class HTTPClient:
    def __init__(
        self,
        *,
        loop: Optional[asyncio.AbstractEventLoop] = None
    ):
        self.__session: Optional[ClientSession] = None
        self.loop = loop

        self.token: Optional[str] = None


    def recreate(self):
        if self.__session is None or self.__session.closed is True:
            self.__session = aiohttp.ClientSession()

    async def ws_connect(self) -> ClientWebSocketResponse:
        gateway_connect_uri = "wss://gateway.discord.gg/?v=9&encoding=json"
        ws = await self.__session.ws_connect(gateway_connect_uri)
        return ws


    async def request(self, route: Route, **kwargs):
        method = route.method
        url = route.url

        headers: Dict[str, str] = {
            "Authorization": self.token
        }

        kwargs["headers"] = headers

        async with self.__session.request(method, url, **kwargs) as resp:
            ...
