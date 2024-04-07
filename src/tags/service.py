from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.tags.models import Tag
from src.tags.schemas import TagCreated


async def create_tag(
    tag_name: str,
    session: AsyncSession,
) -> TagCreated:
    session.add(Tag(name=tag_name))
    await session.commit()
    return TagCreated(**{"tag_name": tag_name})


async def get_tags(session: AsyncSession) -> list[str | Any]:
    res = await session.scalars(select(Tag.name))
    return list(res.all())


async def get_tag_by_name(
    name: str,
    session: AsyncSession,
) -> Tag:
    tag: Tag = await session.scalar(select(Tag).where(Tag.name == name))
    return tag
