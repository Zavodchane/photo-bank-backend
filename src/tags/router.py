from fastapi import APIRouter, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.admins import dependencies as admins_dependencies
from src.admins.models import Admin
from src.database import database
from src.photos.schemas import PhotoAdminSchema
from src.tags import service
from src.tags.schemas import TagCreated
from src.photos import service as photos_service

router = APIRouter()


@router.post(
    "",
    response_model=TagCreated,
    status_code=status.HTTP_201_CREATED,
)
async def create_tag(
    tag_name: str,
    admin: Admin = Depends(admins_dependencies.verify_admin),
    session: AsyncSession = Depends(database.session_dependency),
):
    return await service.create_tag(
        tag_name=tag_name,
        session=session,
    )


@router.get(
    "",
    response_model=list[str],
    status_code=status.HTTP_200_OK,
)
async def get_tags(
    admin: Admin = Depends(admins_dependencies.verify_admin),
    session: AsyncSession = Depends(database.session_dependency),
):
    return await service.get_tags(session=session)


@router.post(
    "/search",
    response_model=list[PhotoAdminSchema],
    status_code=status.HTTP_200_OK,
)
async def get_photos_by_tags(
    tags: list[str],
    session: AsyncSession = Depends(database.session_dependency),
):
    return await photos_service.get_photos_by_tags(
        tags=tags,
        session=session,
    )
