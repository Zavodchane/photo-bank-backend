import enum
from typing import Optional

from pydantic import BaseModel


class PrimaryColor(enum.IntEnum):
    black: int = 0
    white: int = 1
    red: int = 2
    green: int = 3
    blue: int = 4


class Status(enum.IntEnum):
    published: int = 0
    not_published: int = 1
    draft: int = 2


class PhotoSchema(BaseModel):
    name: str

    tags: Optional[list[str]] = None

    has_people: bool

    primary_color: Optional[PrimaryColor] = None

    hash: str
    status: Status

    text_vector: Optional[list[float]] = None
    image_vector: Optional[list[float]] = None

    url: str

    season: Optional[int] = None
    day_time: Optional[int] = None
    orientation: Optional[int] = None
    format: Optional[int] = None

    longitude: Optional[float] = None
    latitude: Optional[float] = None

    slag: str

    height: int
    width: int

    file_size_name: int

    views: int
    download_amount: int
    rating: float


class PhotoUserSchema(BaseModel):
    name: str

    tags: Optional[list[str]] = None

    has_people: bool

    primary_color: Optional[PrimaryColor] = None

    status: Status

    url: str

    season: Optional[int] = None
    day_time: Optional[int] = None
    orientation: Optional[int] = None
    format: Optional[int] = None

    longitude: Optional[float] = None
    latitude: Optional[float] = None

    slag: str

    height: int
    width: int

    rating: float


class PhotoAdminSchema(PhotoUserSchema):
    file_size_name: int

    views: int
    download_amount: int
