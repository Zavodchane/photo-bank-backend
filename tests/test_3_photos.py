import asyncio
import os

from httpx import AsyncClient


admin1: dict = {"username": "BigBoss", "password": "MyLittlePony"}

ACCESS_TOKEN: str

TASK_ID_1: str
TASK_ID_2: str


invalid_photos: list = [
    "./tests/not_photos/dawd.txt",
    "./tests/not_photos/sgsegsegse.txt",
    "./tests/not_photos/jyjgy.txt",
]

invalid_valid_photos: list = [
    "./tests/photos/ARTPLAY.jpeg",
    "./tests/not_photos/dawd.txt",
    "./tests/photos/ARTPLAY_3.jpeg",
]

valid_photos: list = [
    "./tests/photos/ГУМ.JPG",
    "./tests/photos/ГУМ (2).jpg",
    "./tests/photos/ГУМ-каток.jpg",
]


def to_upload(paths: list) -> list:
    files = []
    for file_path in paths:
        if os.path.exists(file_path):
            with open(file_path, "rb") as file:
                files.append(("files", (os.path.basename(file_path), file.read())))
    return files


async def test_login_admin(ac: AsyncClient):
    response = await ac.post(
        "/admins/login",
        json={
            "username": admin1.get("username"),
            "password": admin1.get("password"),
        },
    )
    global ACCESS_TOKEN
    ACCESS_TOKEN = response.json()["access_token"]


async def test_upload_invalid_photo(ac: AsyncClient):
    files = to_upload(invalid_photos)
    response = await ac.post(
        "/admins/photos/upload",
        headers={"Authorization": f"Bearer {ACCESS_TOKEN}"},
        files=files,
    )
    assert response.json()[0]["task_id"] is None
    assert response.json()[1]["task_id"] is None
    assert response.json()[2]["task_id"] is None


async def test_upload_valid_invalid_photo(ac: AsyncClient):
    files = to_upload(invalid_valid_photos)
    response = await ac.post(
        "/admins/photos/upload",
        headers={"Authorization": f"Bearer {ACCESS_TOKEN}"},
        files=files,
    )
    assert response.json()[0]["detail"] is None
    assert response.json()[1]["task_id"] is None
    assert response.json()[2]["detail"] is None
    global TASK_ID_1, TASK_ID_2
    TASK_ID_1 = response.json()[0]["task_id"]
    TASK_ID_2 = response.json()[2]["task_id"]


async def test_uploaded_valid_invalid_photo_get_tasks(ac: AsyncClient):
    response1 = await ac.get(
        f"/tasks/photo/{TASK_ID_1}",
        headers={"Authorization": f"Bearer {ACCESS_TOKEN}"},
    )
    print(response1.json())
    assert response1.json().get("data").get("name") == "ARTPLAY.jpeg"
