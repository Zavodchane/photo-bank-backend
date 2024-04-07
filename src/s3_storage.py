import aioboto3

from src.config import settings


async def get_photo_url(
        file_name: str,
        bucket_name: str = settings.s3_storage.photo_bucket,
        expires: int = settings.s3_storage.expires_photo_url,
) -> str | None:
    session = aioboto3.Session()
    async with session.client(**settings.s3_storage.config) as s3:
        response = await s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket_name, "Key": file_name},
            ExpiresIn=expires,
        )
    return response


async def upload_photo(
        file,
        file_name: str,
        bucket_name: str = settings.s3_storage.photo_bucket,
):
    session = aioboto3.Session()
    async with session.client(**settings.s3_storage.config) as s3:
        await s3.upload_fileobj(
            Fileobj=file,
            Key=file_name,
            Bucket=bucket_name,
        )
