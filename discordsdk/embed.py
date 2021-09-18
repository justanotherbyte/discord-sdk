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

        self.image: Dict[str, str] = {}
        self.thumbnail: Dict[str, str] = {}
        self.author: Dict[str, str] = {}
        self.footer: Dict[str, str] = {}

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
        self.image["url"] = url
        return self
    
    def set_thumbnail(self, *, url: str):
        self.thumbnail["url"] = url
        return self

    def set_author(
        self,
        *,
        name: str,
        url: Optional[str] = None,
        icon_url: Optional[str] = None
    ):
        self.author["name"] = name
        self.author["url"] = name
        self.author["icon_url"] = icon_url

        return self

    def set_footer(
        self,
        *,
        text: str,
        icon_url: Optional[str] = None
    ):
        self.footer["text"] = text
        self.footer["icon_url"] = icon_url

        return self

    def to_dict(self) -> dict:
        array = {
            "title": self.title,
            "description": self.description,
            "color": self.colour,
            "fields": self.fields
        }

        array["image"] = self.image
        array["thumbnail"] = self.thumbnail
        array["author"] = self.author
        array["footer"] = self.footer

        return array

    