from fastapi import APIRouter, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src import Admin
from src.database import database
from src.admins import dependencies as admins_dependencies
from src.tasks.schemas import Response
from src.tasks import service

router = APIRouter()


@router.get(
    "/photo/{task_id}",
    response_model=Response,
    status_code=status.HTTP_200_OK,
)
async def get_photo_status(
    task_id: str,
    admin: Admin = Depends(admins_dependencies.verify_admin),
    session: AsyncSession = Depends(database.session_dependency),
):
    return await service.get_photo_task(
        task_id=task_id,
        admin=admin,
        session=session,
    )
