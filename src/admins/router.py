from typing import List, Any, Optional
from fastapi import APIRouter, status, Depends, UploadFile, File, HTTPException
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from src import Photo
from src.admins import dependencies
from src.admins.schemas import AdminLogin, AdminFilters
from src.admins.utils import NameGenerator as admin_name_generator
from src.admins.models import Admin
from src.admins import dependencies as admins_dependencies
from src.admins import service
from src.auth import service as auth_service
from src.auth import dependencies as auth_dependencies
from src.auth.schemas import Tokens, RefreshToken, AccessToken
from src.cache_memory import cache_memory
from src.database import database
from src.photos.schemas import PhotoAdminSchema
from src.photos import service as photos_service
from src.tasks.schemas import Task

router = APIRouter()


@router.post(
    "/add_admin",
    status_code=status.HTTP_200_OK,
)
async def add_admin(
    admin: AdminLogin,
    session: AsyncSession = Depends(database.session_dependency),
):
    from src.auth import utils as auth_utils

    session.add(
        Admin(
            username=admin.username,
            password=auth_utils.hash_password(admin.password),
        )
    )
    await session.commit()
    return admin


@router.post(
    "/login",
    response_model=Tokens,
    status_code=status.HTTP_200_OK,
)
async def admin_login(
    admin: Admin = Depends(dependencies.verify_login),
    client: Redis = Depends(cache_memory.pool_dependency),
):
    return await auth_service.login(
        user_id=admin.id,
        client=client,
        name_generator=admin_name_generator.refresh_token,
    )


@router.get(
    "/refresh",
    response_model=Tokens,
    status_code=status.HTTP_200_OK,
)
async def admin_refresh(
    refresh_token: RefreshToken = Depends(auth_dependencies.verify_refresh),
    client: Redis = Depends(cache_memory.pool_dependency),
):
    return await auth_service.refresh(
        refresh_token=refresh_token,
        client=client,
        name_generator=admin_name_generator.refresh_token,
    )


@router.get(
    "/logout",
    status_code=status.HTTP_200_OK,
)
async def admin_logout(
    access_token: AccessToken = Depends(auth_dependencies.verify_access),
    client: Redis = Depends(cache_memory.pool_dependency),
):
    await auth_service.logout(
        _id=access_token.sub,
        client=client,
        name_generator=admin_name_generator.refresh_token,
    )


@router.get(
    "/photos",
    response_model=list[PhotoAdminSchema],
    status_code=status.HTTP_200_OK,
)
async def get_all_photos(
    session: AsyncSession = Depends(database.session_dependency),
):
    return await photos_service.get_photos(session=session)


@router.post(
    "/photos/upload",
    response_model=list[Task],
    status_code=status.HTTP_202_ACCEPTED,
)
async def upload_files(
    files: List[UploadFile],
):
    return service.upload_photos(files=files)


@router.post(
    "/photos/search",
    status_code=status.HTTP_200_OK,
)
async def search(
    filters: Optional[AdminFilters] = None,
    text: Optional[str] = None,
):
    return await service.search(text=text, filters=filters)


@router.post(
    "/photos/search_by_photo",
    status_code=status.HTTP_200_OK,
)
async def search(
    file: UploadFile,
):
    return await service.search_by_photo(file=file)


@router.get(
    "/photos/{slag}",
    response_model=PhotoAdminSchema,
    status_code=status.HTTP_200_OK,
)
async def get_photo_by_slag(
    slag: str,
    session: AsyncSession = Depends(database.session_dependency),
):
    photo: Photo | None = await service.get_photo_by_slag(
        slag=slag,
        session=session,
    )
    return PhotoAdminSchema(**photo.__dict__)


@router.post(
    "/photos/{slag}",
    response_model=PhotoAdminSchema,
    status_code=status.HTTP_201_CREATED,
)
async def update_photo_by_slag(
    slag: str,
    updated_data: PhotoAdminSchema,
    admin: Admin = Depends(admins_dependencies.verify_admin),
    session: AsyncSession = Depends(database.session_dependency),
):
    return await service.update_photo_by_slag(
        slag=slag,
        admin=admin,
        updated_data=updated_data,
        session=session,
    )
