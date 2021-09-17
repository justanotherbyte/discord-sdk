from __future__ import annotations

import asyncio

from typing import (
    Optional,
    TYPE_CHECKING,
    Dict,
    List
)

import aiohttp

from .embed import Embed
from .utils import Snowflake, parse_http_response

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

        # state related
        self.application_id: Optional[Snowflake] = None


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
            "Authorization": "Bot " + self.token
        }

        kwargs["headers"] = headers

        async with self.__session.request(method, url, **kwargs) as resp:
            data = await parse_http_response(resp)
            if 300 > resp.status >= 200:
                return data
            
            print("http error")

    def send_message(
        self,
        channel_id: Snowflake,
        content: Optional[str] = None,
        *,
        embed: Optional[Embed] = None,
        embeds: Optional[List[Embed]] = None,
        tts: bool = False
    ):
        if embed and embeds:
            raise ValueError("Cannot use both embed and embeds")

        if embed and not embeds:
            embeds = [embed]
        
        payload = {
            "content": content,
            "embeds": [e.to_dict() for e in embeds],
            "tts": tts
        }

        route = Route("POST", "/channels/{channel_id}/messages", channel_id = channel_id)
        return self.request(route, json = payload)

    def register_slash_command(
        self,
        application_id: Snowflake,
        name: str,
        *,
        description: Optional[str] = None,
        type: Optional[int] = 1,
        guild_id: Optional[int] = None
    ):
        if not guild_id:
            route = Route("POST", "/applications/{application_id}/commands", application_id = application_id)
        else:
            route = Route("POST", "/applications/{application_id}/guilds/{guild_id}/commands", application_id = application_id, guild_id = guild_id)
        
        payload = {
            "name": name,
            "type": type,
            "description": description,
            "options": []
        }
        return self.request(route, json = payload)
