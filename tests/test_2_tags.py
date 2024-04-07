from httpx import AsyncClient
from sqlalchemy import insert

from src import Admin
from src.auth import utils as auth_utils
from tests.conftest import async_session_maker


admin1: dict = {"username": "BigBoss", "password": "MyLittlePony"}

ACCESS_TOKEN: str
REFRESH_TOKEN: str


async def test_login_admin(ac: AsyncClient):
    response = await ac.post(
        "/admins/login",
        json={
            "username": admin1.get("username"),
            "password": admin1.get("password"),
        },
    )
    global ACCESS_TOKEN, REFRESH_TOKEN
    ACCESS_TOKEN = response.json()["access_token"]
    REFRESH_TOKEN = response.json()["refresh_token"]


async def test_get_tags_empty_db(ac: AsyncClient):
    response = await ac.get(
        "/tags",
        headers={"Authorization": f"Bearer {ACCESS_TOKEN}"},
    )
    assert response.status_code == 200
    assert response.json() == []


async def test_create_tags(ac: AsyncClient):
    response = await ac.post(
        "/tags",
        headers={"Authorization": f"Bearer {ACCESS_TOKEN}"},
        params={"tag_name": "Москва"},
    )
    assert response.status_code == 201
    assert response.json()["tag_name"] == "Москва"

    response = await ac.post(
        "/tags",
        headers={"Authorization": f"Bearer {ACCESS_TOKEN}"},
        params={"tag_name": "МГУ"},
    )
    assert response.status_code == 201
    assert response.json()["tag_name"] == "МГУ"


async def test_get_tags(ac: AsyncClient):
    response = await ac.get(
        "/tags",
        headers={"Authorization": f"Bearer {ACCESS_TOKEN}"},
    )
    assert response.status_code == 200
    assert "МГУ" in response.json()
    assert "Москва" in response.json()
