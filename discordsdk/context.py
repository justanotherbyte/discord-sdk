from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    List,
    Optional
)

from .abc import AbstractContext
from .http import Route
from .types import InteractionCallbackType

if TYPE_CHECKING:
    from .ac import ApplicationCommand
    from .embed import Embed


class SlashContext(AbstractContext):
    def __init__(
        self,
        command: ApplicationCommand,
        data: dict
    ):
        self._data = data

        self.command = command
        self.interaction_token = data["token"]
        self.interaction_id = data["id"]
        
    async def send(
        self,
        content: str,
        *,
        embed: Optional[Embed] = None,
        embeds: Optional[List[Embed]] = None
    ):
        if embed and embeds:
            raise ValueError("Cannot pass both embed and embeds kwargs.")

        if embed:
            embeds = [embed]
        
        if embed is None and embeds is None:
            embeds = []
        
        payload = {
            "type": InteractionCallbackType.CHANNEL_MESSAGE_WITH_SOURCE,
            "data": {
                "content": content,
                "embeds": [e.to_dict() for e in embeds]
            }
        }

        route = Route(
            "POST",
            "/interactions/{interaction_id}/{interaction_token}/callback",
            interaction_id = self.interaction_id,
            interaction_token = self.interaction_token
        )

        await self._state.http.request(route, json = payload)