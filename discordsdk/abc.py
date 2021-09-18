from __future__ import annotations

from typing import (
    Optional,
    TYPE_CHECKING,
    List
)

from .utils import _sanitize_embeds, Snowflake

if TYPE_CHECKING:
    from .state import State
    from .embed import Embed

class AbstractContext:
    """
    A class that houses some common methods that all context's will have.
    """
    _state: State # set after context object is created

    async def send(self):
        raise NotImplementedError

class MessageableChannel:
    """
    Common attributes that a messageable channel will have (such as id, guild etc.)
    """
    def __init__(
        self,
        *,
        id: Snowflake
    ):
        self.id = id
    
class Messageable:

    _state: State

    async def _get_channel() -> MessageableChannel:
        ...

    async def send(
        self,
        content: Optional[str] = None,
        *,
        embed: Optional[Embed] = None,
        embeds: Optional[List[Embed]] = None
    ):
        embeds = _sanitize_embeds(embed, embeds)
        channel = await self._get_channel()

        await self._state.http.send_message(
            channel.id,
            content,
            embeds=embed
        )