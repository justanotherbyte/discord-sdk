from typing import (
    Optional,
    Callable
)

from .utils import Snowflake


class ApplicationCommand:
    def __init__(
        self,
        id: Snowflake,
        *,
        application_id: Snowflake,
        name: str,
        description: str,
        version: Snowflake,
        default_permission: bool,
        type: int,
        callback: Callable,
        guild_id: Optional[Snowflake] = None
    ):
        self.id = id
        self.application_id = application_id
        self.name = name
        self.description = description
        self.version = version
        self.default_permission = default_permission
        self.type = type
        self.guild_id = guild_id

        self.callback = callback

    def __repr__(self) -> str:
        fmt = "<ApplicationCommand id={0.id!r} name={0.name!r}>"
        return fmt.format(self)
