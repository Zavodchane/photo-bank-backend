import asyncio
import datetime
from typing import Any, Optional

import httpx
import requests
from fastapi import UploadFile, Depends
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from src import Photo, Tag, PhotosTags
from src.admins.models import Admin
from src.admins.schemas import AdminFilters
from src.auth import exceptions as auth_exceptions
from src.tags import service as tag_service
from src.helpers import helpers
from src.photos.schemas import PhotoAdminSchema
from src.tasks.schemas import Task
from src.tasks import tasks as celery_tasks

from src.photos import exceptions as photos_exceptions


async def get_admin_by_username(
    username: str,
    session: AsyncSession,
) -> Admin:
    admin: Admin = await session.scalar(select(Admin).where(Admin.username == username))
    if admin:
        return admin
    raise auth_exceptions.wrong_login_password


async def get_admin_by_id(
    _id: int | str,
    session: AsyncSession,
) -> Admin:
    admin: Admin = await session.scalar(select(Admin).where(Admin.id == _id))
    if admin:
        return admin
    raise auth_exceptions.token_invalid


def upload_photos(files: list[UploadFile]) -> list[Task]:
    tasks: list = []

    for file in files:
        # TODO: Сделать проверку на дуплиаты с помощью хеша
        if helpers.get_format(file.filename) != 99:
            task_id = celery_tasks.upload_photo.delay(
                file=file.file.read(), filename=file.filename
            )
            tasks.append(Task(task_id=str(task_id)))
        else:
            tasks.append(Task(detail=photos_exceptions.invald_format.detail))
    return tasks


async def get_photo_by_slag(  # TODO: Tests
    slag: str,
    session: AsyncSession,
) -> Photo | None:
    photo: Photo = await session.scalar(
        select(Photo).where(Photo.slag == slag).options(selectinload(Photo.tags))
    )
    return photo


async def update_photo_by_slag(  # TODO: Write and tests
    slag: str,
    admin: Admin,
    updated_data: PhotoAdminSchema,
    session: AsyncSession,
) -> PhotoAdminSchema:
    photo: Photo = await get_photo_by_slag(
        slag=slag,
        session=session,
    )
    photo.name = updated_data.name
    photo.status = updated_data.status
    photo.tags = updated_data.tags
    photo.day_time = updated_data.day_time
    photo.season = updated_data.season
    photo.has_people = updated_data.has_people
    photo.primary_color = updated_data.primary_color
    photo.longitude = updated_data.longitude
    photo.latitude = updated_data.latitude
    photo.updated_by = admin.id
    photo.updated_at = datetime.datetime.utcnow()
    await session.commit()
    return PhotoAdminSchema(**photo.__dict__)


async def search(
    filters: AdminFilters,
    text: Optional[str] = None,
):
    response = requests.post(
        "http://localhost:8001/api/v1/model/find_images",
        json=filters.model_dump(),
        params={"text": text},
    )
    return response.json()


async def search_by_photo(file: UploadFile):
    response = requests.post(
        "http://localhost:8001/api/v1/model/find_images_photo",
        files={"file": file.file},
    )
    return response.json()


async def create_photo(
    admin: Admin,
    data: dict,
    session: AsyncSession,
) -> Photo:

    data["height"] = int(data["height"])
    data["width"] = int(data["width"])
    data["created_by"] = str(admin.id)
    data["updated_by"] = str(admin.id)

    tags: list[str] | None = data.pop("tags")

    photo: Photo = Photo(**data)
    session.add(photo)
    await session.commit()

    if not tags:
        return photo

    tags_in_db = await tag_service.get_tags(session=session)
    tags_l: list[Tag] = []
    for t in tags:

        if t in tags_in_db:
            tag: Tag = await tag_service.get_tag_by_name(name=t, session=session)

        else:
            tag: Tag = Tag(name=t)
            session.add(tag)

        tags_l.append(tag)

    await session.commit()

    for tag in tags_l:
        session.add(PhotosTags(tag_id=tag.id, photo_id=photo.id))
    await session.commit()

    return photo


async def get_photo_by_hash(
    hash: str,
    session: AsyncSession,
) -> Photo:
    photo: Photo = await session.scalar(
        select(Photo).where(Photo.hash == hash).options(selectinload(Photo.tags))
    )
    return photo
