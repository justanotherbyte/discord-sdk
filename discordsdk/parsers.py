from typing import Any


class EventParser:
    def __init__(
        self,
        event_name: str,
        data: dict
    ):
        self.event_name = event_name
        self.data = data.get("d") or data

    async def convert(self) -> Any:
        raise NotImplementedError

class MESSAGE_CREATE(EventParser):
    async def convert(self):
        ...