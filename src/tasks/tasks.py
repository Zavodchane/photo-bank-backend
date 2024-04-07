import io
import logging
import uuid
import requests

from celery import Celery

from src.config import settings
from src.helpers import helpers
from src.photos.schemas import Status

celery = Celery(
    "tasks",
    backend=settings.celery.backend,
    broker=settings.celery.broker,
)


@celery.task
def upload_photo(file, filename):
    contents = file
    format = helpers.get_format(filename)
    file_hash = helpers.get_hash(contents)
    # todo проверить хеш на наличие в бд если в он в бд можно стопить
    file_size, size_category, orientation = helpers.get_file_size_name_orientation(
        contents
    )

    split = file_size.split("x")
    width: int = int(split[0])
    height: int = int(split[1])
    # получаем все метаданные, используем их для получения информации
    metadata = helpers.get_metadata(contents)

    coords = helpers.get_coords(metadata)
    longitude = coords["Longitude"]
    latitude = coords["Latitude"]

    slug = helpers.generate_slug(filename, str(uuid.uuid4()))

    timeobj = helpers.get_timeobj(metadata)

    timeday = helpers.get_time_day(timeobj)
    season = helpers.get_season(timeobj)

    views = 0
    download_amount = 0
    rating = 0
    primary_color = helpers.get_color(file)

    text_vector, image_vector, tags = get_all(
        filename=filename,
        content=contents,
    )

    if "person" in tags:
        has_people = True
    else:
        has_people = False

    photo = {
        "name": filename,
        "tags": tags,
        "has_people": has_people,
        "primary_color": primary_color,
        "hash": file_hash,
        "status": Status.draft,
        "text_vector": text_vector,
        "image_vector": image_vector,
        "season": season,
        "day_time": timeday,
        "orientation": orientation,
        "format": format,
        "longitude": longitude,
        "latitude": latitude,
        "slag": slug,
        "height": height,
        "width": width,
        "file_size_name": size_category,
        "views": views,
        "download_amount": download_amount,
        "rating": rating,
        "contents": contents,
    }
    return photo


def get_all(filename: str, content: bytes) -> (list[float], list[float], list[str]):
    response = requests.post(
        settings.ai_api.url_all,
        files={"content": io.BytesIO(content)},
        params={"filename": filename},
    )
    logging.info(response.json())
    text_vector: list[float] = response.json()["vector_text"]
    image_vector: list[float] = response.json()["vector_img"]
    tags: list[str] = response.json()["tags"]
    return text_vector, image_vector, tags
