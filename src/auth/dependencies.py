from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jwt import DecodeError

from src.auth import utils, exceptions
from src.auth.schemas import AccessToken, RefreshToken

http_bearer = HTTPBearer()


def get_data_from_token(token: str) -> dict:
    try:
        data = utils.decode_jwt(token=token)
        return data
    except DecodeError:
        raise exceptions.token_invalid


def verify_access(
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
) -> AccessToken:
    token = credentials.credentials
    data = get_data_from_token(token=token)
    return AccessToken(**data)


def verify_refresh(
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
) -> RefreshToken:
    token = credentials.credentials

    data = get_data_from_token(token=token)

    if data.get("id") is None:
        raise exceptions.token_invalid

    return RefreshToken(**data)
