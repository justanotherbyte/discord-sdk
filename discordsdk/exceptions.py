from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from aiohttp import ClientResponse


class HTTPException(Exception):
    """
    HTTP Based exceptions
    """
    def __init__(self, resp: ClientResponse, data: dict):
        self.resp = resp
        self.status = resp.status
        self.data = data
        self.reason = resp.reason

    def __str__(self) -> str:
        fmt = "{0.status}: {0.reason}: {0.data}"
        return fmt.format(self)

class CommandException(Exception):
    """
    Command Based exceptions
    """
    def __init__(self, command_name: str, original_error: Exception):
        self.name = command_name
        self.original = original_error

    def __str__(self) -> str:
        fmt = "Command {0.name!r} raised an error: {0.original!r}"
        return fmt.format(self)