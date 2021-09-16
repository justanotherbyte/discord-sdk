from __future__ import annotations

import sys
import json
import threading
import time
import asyncio

from typing import (
    Optional,
    TYPE_CHECKING,
    Union
)

import aiohttp

if TYPE_CHECKING:
    from aiohttp import ClientWebSocketResponse
    from aiohttp.http_websocket import WSMessage

    from .client import Client
    _NUMBER = Union[float, int]


class WebSocketClosure(Exception):
    ...

class ReconnectWebSocket(Exception):
    def __init__(self, session_id, sequence, *, resume=False):
        self.session_id = session_id
        self.sequence = sequence
        self.op = "READY" if resume is False else "RESUME"

class HeartbeatHandler(threading.Thread):
    def __init__(self, *args, **kwargs):
        self.socket = kwargs.pop("socket")
        self.interval: _NUMBER = kwargs.pop("interval")

        threading.Thread.__init__(self, *args, **kwargs)

        self._last_ack = time.perf_counter()
        self._last_recv = time.perf_counter()
        self._last_send = time.perf_counter()

        self._stop_ev = threading.Event()
        
        self.daemon = True

    def run(self):
        while not self._stop_ev.wait(self.interval):
            heartbeat_payload = self.get_heartbeat_payload()
            f = asyncio.run_coroutine_threadsafe(self.socket.send_as_json(heartbeat_payload), loop = self.socket.loop)

            f.result()

    def get_heartbeat_payload(self) -> dict:
        payload = {
            "op": self.socket.HEARTBEAT,
            "d": self.socket.sequence
        }

        return payload

    def ack(self):
        ack_time = time.perf_counter()
        self._last_ack = ack_time
        self._last_recv = ack_time

    def stop(self):
        self._stop_ev.set()
    

class DiscordWebSocket:
    DISPATCH           = 0
    HEARTBEAT          = 1
    IDENTIFY           = 2
    PRESENCE           = 3
    VOICE_STATE        = 4
    VOICE_PING         = 5
    RESUME             = 6
    RECONNECT          = 7
    REQUEST_MEMBERS    = 8
    INVALIDATE_SESSION = 9
    HELLO              = 10
    HEARTBEAT_ACK      = 11
    GUILD_SYNC         = 12

    def __init__(self, ws, *, loop):
        self.socket: ClientWebSocketResponse = ws
        self.loop: asyncio.AbstractEventLoop = loop

        self.close_code: Optional[int] = None
        self.sequence: Optional[int] = None
        self.session_id: Optional[str] = None
        self._heartbeat = None


        # dynamically set attributes
        self.token: Optional[str] = None
        self.client: Optional[Client] = None
        self._max_heartbeat_timeout: Optional[_NUMBER] = None


    @classmethod
    async def from_client(cls, client: Client, ws: ClientWebSocketResponse, loop: asyncio.AbstractEventLoop):
        socket = cls(ws, loop = loop)
        socket.token = client.http.token
        socket.client = client

        await socket.poll_socket()

        return socket

    async def identify(self):
        payload = {
            "op": self.IDENTIFY,
            "d": {
                "token": self.token,
                "intents": 513,
                "properties": {
                    "$os": sys.platform,
                    "$browser": "discordsdk"
                }
            }
        }

        await self.send_as_json(payload)

    async def resume(self):
        payload = {
            "op": self.RESUME,
            "d": {
                "token": self.token,
                "session_id": self.session_id,
                "seq": str(self.sequence)
            }
        }

        await self.send_as_json(payload)

    async def send_as_json(self, data):
        data = json.dumps(data)
        try:
            await self.socket.send_str(data)
        except RuntimeError as _:
            if not self._can_handle_close():
                raise WebSocketClosure

    def _can_handle_close(self) -> bool:
        code = self.close_code or self.socket.close_code
        return code not in {1000, 4004, 4010, 4011, 4012, 4013, 4014}

    async def poll_socket(self):
        try:
            msg = await self.socket.receive(timeout = self._max_heartbeat_timeout)
            if msg.type is aiohttp.WSMsgType.TEXT:
                await self.handle_message(msg)
            elif msg.type is aiohttp.WSMsgType.BINARY:
                await self.handle_message(msg)
            elif msg.type is aiohttp.WSMsgType.ERROR:
                print("error packet")
            elif msg.type in (aiohttp.WSMsgType.CLOSED, aiohttp.WSMsgType.CLOSE, aiohttp.WSMsgType.CLOSING):
                raise WebSocketClosure
        except (asyncio.TimeoutError, WebSocketClosure) as exc:
            if self._heartbeat:
                # we no longer want to continue sending heartbeats in the event of a websocket issue.
                self._heartbeat.stop()
                self._heartbeat = None
            if isinstance(exc, asyncio.TimeoutError):
                # the connection dropped for some reason, attempt a re-connect
                raise ReconnectWebSocket from exc
            
            if isinstance(exc, WebSocketClosure):
                # the connection closed
                if self._can_handle_close():
                    raise ReconnectWebSocket(self.session_id, self.sequence, resume=True)
                raise ReconnectWebSocket(self.session_id, self.sequence)

    async def handle_message(self, message: WSMessage, *, debug: bool = False):
        msg = message.json()

        if debug is True:
            print(msg)

        op: int = msg.get("op")
        data: dict = msg.get("d")
        event: Optional[str] = msg.get("t")
        seq: Optional[str] = msg.get("s")

        if seq is not None:
            self.sequence = seq

        if op != self.DISPATCH:
            if op == self.HELLO:
                interval = data["heartbeat_interval"] / 1000.0
                self._max_heartbeat_timeout = interval
                heartbeat = HeartbeatHandler(socket = self, interval = interval)
                heartbeat.start()

                await self.identify()

            if op == self.HEARTBEAT:
                heartbeat = self._heartbeat
                if heartbeat:
                    payload = heartbeat.get_heartbeat_payload()
                    await self.send_as_json(payload)

            if op == self.HEARTBEAT_ACK:
                heartbeat = self._heartbeat
                if heartbeat:
                    heartbeat.ack()

        if event == "READY":
            self.sequence = msg["s"]
            self.session_id = data["session_id"]


        # our last priority is notifying the client of a received event
        await self.client._notify_event(event, msg)
            
    async def close(self):
        if self._heartbeat:
            self._heartbeat.stop()

        await self.socket.close(code = 4000)