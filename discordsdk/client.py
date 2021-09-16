import asyncio

from typing import (
    Coroutine,
    Optional,
    Dict,
    List
)

from .gateway import DiscordWebSocket
from .http import HTTPClient
from .events import EventListener


class Client:
    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self.http = HTTPClient(loop = self.loop)

        self.ws: Optional[DiscordWebSocket] = None

        # caches
        self.__event_listeners: Dict[str, List[EventListener]] = {}


    async def connect(self, token: str):
        self.http.token = token
        self.http.recreate() # initial session creation
        aiohttp_ws = await self.http.ws_connect()
        ws = await DiscordWebSocket.from_client(self, aiohttp_ws, loop = self.loop)
        self.ws = ws

        while True:
            await self.ws.poll_socket()

    def listen(self, name: str):
        def inner(func: Coroutine):
            listeners = self.__event_listeners.get(name, [])
            listener = EventListener(name, func)
            listeners.append(listener)
            self.__event_listeners[name] = listeners

        return inner

    async def _notify_event(self, event_name: str, data: dict):
        try:
            listeners = self.__event_listeners[event_name]
            for listener in listeners:
                await listener.run_callback(data)
        except KeyError:
            pass

    def run(self, token: str):
        token = token.strip() # removes extra whitespaces and raises an error if the token is a 'NoneType' or any other type.
        self.loop.run_until_complete(self.connect(token))
        self.loop.run_forever()