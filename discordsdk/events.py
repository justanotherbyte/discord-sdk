from typing import Coroutine


class EventListener:
    def __init__(self, gateway_event_name: str, callback: Coroutine):
        self.event_name = gateway_event_name
        self.callback = callback

    async def run_callback(self, raw_data: dict):
        return await self.callback(raw_data)