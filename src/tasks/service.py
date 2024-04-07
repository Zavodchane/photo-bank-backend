from io import BytesIO

from celery.result import AsyncResult
from sqlalchemy.ext.asyncio import AsyncSession

from src import s3_storage, Photo, Admin
from src.admins import service as admins_service
from src.photos.schemas import PhotoAdminSchema
from src.photos import service as photos_service
from src.tasks.schemas import Response, Status


async def get_photo_task(
    task_id: str,
    admin: Admin,
    session: AsyncSession,
) -> Response:
    task = AsyncResult(task_id)

    if not task.ready():
        return Response(
            data={"task_id": task_id, "detail": str(task.traceback)},
            status=Status.in_progress,
        )

    photo_data: dict = task.get()

    photo: Photo = await admins_service.get_photo_by_hash(
        hash=photo_data["hash"],
        session=session,
    )
    if photo is not None:
        photo_dict = photo.__dict__
        tags = photo_dict.pop("tags")
        tags = [tag.name for tag in tags]
        return Response(
            data=PhotoAdminSchema(**photo_dict, tags=tags).model_dump(),
            status=Status.completed,
        )

    await s3_storage.upload_photo(
        file=BytesIO(photo_data.pop("contents")),
        file_name=photo_data.get("slag"),
    )

    url = await s3_storage.get_photo_url(file_name=photo_data.get("slag"))
    photo_data["url"] = url

    photo: Photo = await admins_service.create_photo(
        admin=admin,
        data=photo_data,
        session=session,
    )

    return Response(
        data=PhotoAdminSchema(**photo.__dict__).model_dump(),
        status=Status.completed,
    )
