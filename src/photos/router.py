from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.admins.schemas import UserFilters
from src.photos import service
from src.database import database
from src.photos.schemas import PhotoUserSchema

router = APIRouter()


@router.post(
    "/similar/{slag}",
    response_model=list[PhotoUserSchema],
    status_code=status.HTTP_200_OK,
)
async def get_similar_photo(
    photo_user: PhotoUserSchema,
    session: AsyncSession = Depends(database.session_dependency),
):
    return await service.get_similar_photo(
        photo_user=photo_user,
        session=session,
    )


@router.get(
    "/search",
    response_model=list[PhotoUserSchema],
    status_code=status.HTTP_200_OK,
)
async def search_photo_by_filter(
    filters: UserFilters,
    filename: str | None = None,
    session: AsyncSession = Depends(database.session_dependency),
):
    return await service.search_photos_by_filename_filters(
        filename=filename,
        filters=filters,
        session=session,
    )


@router.post("/{slag}/translate")
async def get_translate_photo(
    slag: str,
    session=Depends(database.session_dependency),
):
    return await service.get_translate_photo(
        slag=slag,
        session=session,
    )


@router.get(
    "/{slag}",
    response_model=PhotoUserSchema,
    status_code=status.HTTP_200_OK,
)
async def get_photo_by_slag(
    slag: str,
    session: AsyncSession = Depends(database.session_dependency),
):
    return await service.get_photo_by_slag(
        slag=slag,
        session=session,
    )
