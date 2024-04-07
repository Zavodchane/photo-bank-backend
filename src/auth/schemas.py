from pydantic import BaseModel


class AccessToken(BaseModel):
    sub: str


class RefreshToken(AccessToken):
    id: str


class Tokens(BaseModel):
    access_token: str
    refresh_token: str
    type: str = "Bearer"
