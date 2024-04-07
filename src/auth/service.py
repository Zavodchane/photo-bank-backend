import uuid
from typing import Callable

from redis.asyncio import Redis

from src.auth import utils, exceptions
from src.auth.schemas import RefreshToken
from src.config import settings


async def login(
    user_id: int | str | uuid.UUID,
    client: Redis,
    name_generator: Callable,
):
    _id = str(user_id)
    refresh_token_id = str(uuid.uuid4())

    saved: bool = await client.set(
        name=name_generator(_id=_id),
        value=refresh_token_id,
        ex=settings.redis.refresh_token_expire_seconds,
    )

    if not saved:
        raise exceptions.iam_teapot  # TODO: haha, It's just a joke.

    return utils.tokens_info(
        user_id=_id,
        refresh_token_id=refresh_token_id,
    )


async def refresh(
    refresh_token: RefreshToken,
    client: Redis,
    name_generator: Callable,
):
    refresh_token_id = str(uuid.uuid4())

    deleted = await client.delete(name_generator(_id=refresh_token.sub))

    if not deleted:
        raise exceptions.token_invalid

    return utils.tokens_info(
        user_id=refresh_token.sub,
        refresh_token_id=refresh_token_id,
    )


async def logout(
    _id: int | str | uuid.UUID,
    client: Redis,
    name_generator: Callable,
):
    await client.delete(name_generator(_id=_id))
