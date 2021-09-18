from __future__ import annotations

import json

from typing import (
    TYPE_CHECKING,
    Optional,
    Union
)

if TYPE_CHECKING:
    from aiohttp import ClientResponse


Snowflake = Union[int, str]

async def parse_http_response(response: ClientResponse) -> Optional[dict]:
    content = await response.text()
    try:
        return json.loads(content)
    except Exception:
        return None


def _sanitize_embeds(embed, embeds):
        if embed and embeds:
            raise ValueError("Cannot pass both embed and embeds kwargs.")

        if embed:
            embeds = [embed]
        
        if embed is None and embeds is None:
            embeds = []

        return embeds