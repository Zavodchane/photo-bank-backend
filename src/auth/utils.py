from datetime import timedelta, datetime
from typing import Any

import bcrypt
import jwt
from jwt import ExpiredSignatureError

from src.auth import exceptions
from src.config import settings
from src.auth.schemas import (
    Tokens,
    RefreshToken,
    AccessToken,
)


def encode_jwt(
    payload: dict,
    expire_minutes: int,
    private_key: str = settings.auth_jwt.private_key_path.read_text(),
    algorithm: str = settings.auth_jwt.algorithm,
) -> str:
    to_encode = payload.copy()
    now = datetime.utcnow()
    expire = now + timedelta(minutes=expire_minutes)
    to_encode.update(
        exp=expire,
        iat=now,
    )
    encoded = jwt.encode(
        payload=to_encode,
        key=private_key,
        algorithm=algorithm,
    )
    return encoded


def decode_jwt(
    token: str | bytes,
    public_key: str = settings.auth_jwt.public_key_path.read_text(),
    algorithm: str = settings.auth_jwt.algorithm,
):
    try:
        return jwt.decode(
            jwt=token,
            key=public_key,
            algorithms=[algorithm],
        )

    except ExpiredSignatureError:
        raise exceptions.token_expired


def hash_password(
    password: str,
) -> bytes:
    return bcrypt.hashpw(
        password=password.encode(),
        salt=bcrypt.gensalt(),
    )


def verify_password(
    password: str,
    hashed_password: bytes,
) -> bool:
    return bcrypt.checkpw(
        password=password.encode(),
        hashed_password=hashed_password,
    )


def tokens_info(user_id: str, refresh_token_id: str) -> Tokens:

    access_token = encode_jwt(
        payload=AccessToken(sub=user_id).model_dump(),
        expire_minutes=settings.auth_jwt.access_token_expire_minutes,
    )

    refresh_token = encode_jwt(
        payload=RefreshToken(sub=user_id, id=refresh_token_id).model_dump(),
        expire_minutes=settings.auth_jwt.refresh_token_expire_minutes,
    )

    return Tokens(
        access_token=access_token,
        refresh_token=refresh_token,
    )
