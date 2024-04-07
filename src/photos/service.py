from typing import Any

import requests
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.admins.schemas import UserFilters
from src.photos.models import Photo
from src.photos.schemas import PhotoUserSchema, Status, PhotoAdminSchema


async def get_photo_by_slag(
    slag: str,
    session: AsyncSession,
) -> PhotoUserSchema | None:
    photo: Photo = await session.scalar(
        select(Photo)
        .where(Photo.slag == slag and Photo.status == Status.published)
        .options(selectinload(Photo.tags))
    )
    if photo is None:
        return None
    return PhotoUserSchema(**photo.__dict__)


async def get_similar_photo(
    photo_user: PhotoUserSchema,
    session: AsyncSession,
):  # TODO: Write and tests
    result = await session.scalars(
        select(Photo).options(selectinload(Photo.similar_photos))
    )
    return result.all()


async def get_photos(session: AsyncSession):
    result = await session.scalars(select(Photo).options(selectinload(Photo.tags)))
    photos: list = []
    for photo in list(result.all()):
        photo = photo.__dict__
        tags = photo.pop("tags")
        tags = [tag.name for tag in tags]
        photos.append(PhotoAdminSchema(**photo, tags=tags))
    return photos


async def search_photos_by_filename_filters(
    filters: UserFilters,
    session: AsyncSession,
    filename: str | None = None,
) -> list[PhotoAdminSchema]:
    query = select(Photo)
    if filters.season is not None:
        query = query.where(Photo.season == filters.season)

    if filters.day_time is not None:
        query = query.where(Photo.day_time == filters.day_time)

    if filters.orientation is not None:
        query = query.where(Photo.orientation == filters.orientation)

    if filters.format is not None:
        query = query.where(Photo.format == filters.format)

    if filters.file_size_name is not None:
        query = query.where(Photo.file_size_name == filters.file_size_name)

    if filters.has_people is not None:
        query = query.where(Photo.has_people == filters.has_people)

    if filters.primary_color is not None:
        query = query.where(Photo.primary_color == filters.primary_color)

    query = query.where(Photo.status == Status.published)

    result = await session.scalars(query)
    photos = [PhotoAdminSchema(**photo.__dict__) for photo in list(result.all())]

    if filename is None:
        return photos

    # TODO: find_images
    return photos


async def get_photos_by_tags(
    tags: list[str],
    session: AsyncSession,
) -> list[PhotoAdminSchema]:
    photos = await session.scalars(select(Photo).options(selectinload(Photo.tags)))
    photos = photos.all()

    photos_schema: list = []
    for photo in photos:
        tags_db = [tag.name for tag in photo.tags]
        if tags_db != tags:
            continue
        photo = photo.__dict__
        photo.pop("tags")
        photos_schema.append(
            PhotoAdminSchema(
                **photo,
                tags=tags,
            )
        )
    return photos_schema


async def get_translate_photo(
    slag: str,
    session: AsyncSession,
):
    photo: Photo = await session.scalar(select(Photo).where(Photo.slag == slag))
    response = requests.post(
        "http://127.0.0.1:8001/api/v1/model/translate", params={"URL": photo.url}
    )
    return response.json()
