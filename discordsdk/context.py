from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    List,
    Optional
)

from .abc import AbstractContext
from .http import Route
from .types import InteractionCallbackType
from .webhooks import Webhook
from .state import State
from .utils import _sanitize_embeds

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
        content: Optional[str] = None,
        *,
        embed: Optional[Embed] = None,
        embeds: Optional[List[Embed]] = None
    ):
        
        embeds = _sanitize_embeds(embed, embeds)
        
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

    async def edit_initial(
        self,
        content: Optional[str] = None,
        *,
        embed: Optional[Embed] = None,
        embeds: Optional[List[Embed]] = None
    ):
        embeds = _sanitize_embeds(embed, embeds)

        hook = Webhook(
            "/webhooks/{application_id}/{interaction_token}/messages/@original",
            application_id = self._state.http.application_id,
            interaction_token = self.interaction_token
        )

        hook._state = State.from_state(self._state)

        payload = {
            "content": content,
            "embeds": [e.to_dict() for e in embeds]
        }

        return await hook.PATCH(json = payload)

    async def delete_initial(self):
        hook = Webhook(
            "/webhooks/{application_id}/{interaction_token}/messages/@original",
            application_id = self._state.http.application_id,
            interaction_token = self.interaction_token
        )

        hook._state = State.from_state(self._state)

        return await hook.DELETE()

    async def post_followup(
        self,
        content: str,
        *,
        embed: Optional[Embed] = None,
        embeds: Optional[List[Embed]] = None
    ):
        embeds = _sanitize_embeds(embed, embeds)
        
        hook = Webhook(
            "/webhooks/{application_id}/{interaction_token}",
            application_id = self._state.http.application_id,
            interaction_token = self.interaction_token
        )
        
        hook._state = State.from_state(self._state)

        payload = {
            "content": content,
            "embeds": [e.to_dict() for e in embeds]
        }

        return await hook.POST(json = payload)


    