from typing import (
    Optional,
    List,
    Dict
)


class Embed:
    def __init__(
        self,
        *,
        title: Optional[str] = None,
        description: Optional[str] = None,
        colour: Optional[int] = None,
        color: Optional[int] = None
    ):
        self.title = title
        self.description = description
        self.colour = colour or color

        self.image_url: Optional[str] = None
        self.fields: List[Dict[str, str]] = []

    def add_field(self, *, name: str, value: str, inline: bool = False):
        array = {
            "name": name,
            "value": value,
            "inline": inline
        }

        self.fields.append(array)
        return self

    def set_image(self, *, url: str):
        self.image_url = url
        return self

    def to_dict(self) -> dict:
        array = {
            "title": self.title,
            "description": self.description,
            "color": self.colour,
            "fields": self.fields
        }

        if self.image_url:
            image_array = {
                "url": self.image_url
            }

            array["image"] = image_array
        return array