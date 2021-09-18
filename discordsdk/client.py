import asyncio

from typing import (
    Callable,
    Optional,
    Dict,
    List
)

from .gateway import DiscordWebSocket, WebSocketClosure, ReconnectWebSocket
from .http import HTTPClient
from .events import EventListener
from .utils import Snowflake
from .ac import ApplicationCommand
from .context import SlashContext
from .state import State
from .exceptions import CommandException

class Client:
    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self.http = HTTPClient(loop = self.loop)

        self.ws: Optional[DiscordWebSocket] = None

        # caches
        self.__event_listeners: Dict[str, List[EventListener]] = {}
        self.__pending_application_commands: List[dict] = []

        self.application_commands: Dict[Snowflake, ApplicationCommand] = {}
        
        self._ready_ev = asyncio.Event()


    async def connect(self, token: str):
        self.http.token = token
        self.http.recreate() # initial session creation
        aiohttp_ws = await self.http.ws_connect()
        ws = await DiscordWebSocket.from_client(self, aiohttp_ws, loop = self.loop)
        self.ws = ws

        while True:
            try:
                await self.ws.poll_socket()
            except (WebSocketClosure, ReconnectWebSocket) as ws_exc:
                if isinstance(ws_exc, WebSocketClosure):
                    self.loop.stop()
                
                if isinstance(ws_exc, ReconnectWebSocket):
                    if ws_exc.op == "RESUME":
                        await self.ws.resume()
                    elif ws_exc.op == "IDENTIFY":
                        await self.ws.close()
                        
                        aiohttp_ws = await self.http.ws_connect()
                        ws = await DiscordWebSocket.from_client(self, aiohttp_ws, loop = self.loop)
                        self.ws = ws
                    

    def listen(self, name: str):
        def inner(func: Callable):
            if not asyncio.iscoroutinefunction(func):
                raise ValueError("Listener must have an async callback.")

            listeners = self.__event_listeners.get(name, [])
            listener = EventListener(name, func)
            listeners.append(listener)
            self.__event_listeners[name] = listeners

        return inner

    def slash_command(
        self,
        *,
        name: Optional[str] = None,
        description: Optional[str] = "No Description",
        type: Optional[int] = 1,
        guild_ids: Optional[List[Snowflake]] = None
    ):
        def inner(func: Callable):
            if not asyncio.iscoroutinefunction(func):
                raise ValueError("Application Command must have an async callback.")

            command_name = name or func.__name__
            data = {
                "name": command_name,
                "type": type,
                "description": description,
                "guilds": guild_ids,
                "_callback": func
            }
            self.__pending_application_commands.append(data)

        return inner


    async def _notify_event(self, event_name: str, data: dict):
        try:
            listeners = self.__event_listeners[event_name]
            for listener in listeners:
                await listener.run_callback(data)
        except KeyError:
            pass

    async def register_application_commands(self):
        # publicy avaible api for subclasses
        for data in self.__pending_application_commands:
            name = data["name"]
            description = data["description"]
            type = data["type"]
            guilds = data["guilds"]
            _callback = data["_callback"]
            
            if guilds is None:
                response = await self.http.register_slash_command(
                    self.http.application_id,
                    name,
                    description=description,
                    type=type
                )
                response["callback"] = _callback
                self._create_application_command_object(response)
            else:
                for guild_id in guilds:
                    response = await self.http.register_slash_command(
                        self.http.application_id,
                        name,
                        description=description,
                        type=type,
                        guild_id=guild_id
                    )
                    response["callback"] = _callback
                    self._create_application_command_object(response)

        self.__pending_application_commands = []

    async def process_application_commands(self, event_data: dict):
        guild_id = event_data["guild_id"]
        d = event_data["data"]
        command_id = d["id"]

        command_key = "{command_id}:{guild_id}".format(command_id = command_id, guild_id = guild_id)
        command = self.application_commands.get(command_key)
        if command is None:
            return
        
        ctx = SlashContext(command, event_data)
        state = State(client=self, http=self.http)
        ctx._state = state

        try:
            await command.callback(ctx)
        except Exception as exc:
            raise CommandException(command.name, exc)


    def _create_application_command_object(self, data: dict) -> ApplicationCommand:
        _id = data["id"]
        data.pop("id", None)
        obj = ApplicationCommand(_id, **data)
        key = "{0.id}:{0.guild_id}".format(obj)
        self.application_commands[key] = obj
        return obj


    def run(self, token: str):
        token = token.strip() # removes extra whitespaces and raises an error if the token is a 'NoneType' or any other type.
        self.loop.run_until_complete(self.connect(token))
        self.loop.run_forever()