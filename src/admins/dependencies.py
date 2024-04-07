from fastapi import Depends
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.admins import service
from src.auth import utils as auth_utils
from src.auth import exceptions as auth_exceptions
from src.auth import dependencies as auth_dependencies
from src.admins.models import Admin
from src.admins.schemas import AdminLogin
from src.auth.schemas import AccessToken
from src.database import database


http_bearer = HTTPBearer()


async def verify_login(
    admin_login: AdminLogin,
    session: AsyncSession = Depends(database.session_dependency),
) -> Admin:
    admin: Admin = await service.get_admin_by_username(
        username=admin_login.username, session=session
    )

    if not auth_utils.verify_password(
        password=admin_login.password,
        hashed_password=admin.password,
    ):
        raise auth_exceptions.wrong_login_password

    if admin.is_active:
        return admin

    raise auth_exceptions.user_inactive


async def verify_admin(
    access_token: AccessToken = Depends(auth_dependencies.verify_access),
    session: AsyncSession = Depends(database.session_dependency),
) -> Admin:
    return await service.get_admin_by_id(
        _id=access_token.sub,
        session=session,
    )
