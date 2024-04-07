from typing import Optional

from pydantic import BaseModel


class AdminLogin(BaseModel):
    username: str
    password: str


class UserFilters(BaseModel):
    season: Optional[int] = None
    day_time: Optional[int] = None
    orientation: Optional[int] = None
    format: Optional[int] = None
    file_size_name: Optional[int] = None
    has_people: Optional[bool] = None
    primary_color: Optional[int] = None


class AdminFilters(UserFilters):
    status: Optional[int] = None
