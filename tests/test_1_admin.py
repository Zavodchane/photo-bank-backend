from httpx import AsyncClient
from sqlalchemy import insert

from src import Admin
from src.auth import utils as auth_utils
from tests.conftest import async_session_maker


admin1: dict = {"username": "BigBoss", "password": "MyLittlePony"}

ACCESS_TOKEN: str
REFRESH_TOKEN: str


async def test_create_admin():
    data: dict = {}
    async with async_session_maker() as session:
        data["username"] = admin1["username"]
        data["password"] = auth_utils.hash_password(admin1["password"])
        await session.execute(insert(Admin).values(**data))
        await session.commit()


async def test_login_invalid_username(ac: AsyncClient):
    response = await ac.post(
        "/admins/login",
        json={
            "username": "Vladomer",
            "password": admin1.get("password"),
        },
    )
    print(response.json())
    assert response.status_code == 401
    assert "Invalid username or password" in response.json()["detail"]


async def test_login_invalid_password(ac: AsyncClient):
    response = await ac.post(
        "/admins/login",
        json={
            "username": admin1.get("username"),
            "password": "12345",
        },
    )

    assert response.status_code == 401
    assert "Invalid username or password" in response.json()["detail"]


async def test_login(ac: AsyncClient):
    global ACCESS_TOKEN, REFRESH_TOKEN
    response = await ac.post(
        "/admins/login",
        json={
            "username": admin1.get("username"),
            "password": admin1.get("password"),
        },
    )
    assert response.status_code == 200
    assert "access_token" in response.json().keys()
    assert "refresh_token" in response.json().keys()

    ACCESS_TOKEN = response.json()["access_token"]
    REFRESH_TOKEN = response.json()["refresh_token"]


async def test_refresh_use_access_token(ac: AsyncClient):
    response = await ac.get(
        "/admins/refresh",
        headers={"Authorization": f"Bearer {ACCESS_TOKEN}"},
    )
    assert response.status_code == 400
    assert "Token invalid" in response.json()["detail"]


async def test_refresh(ac: AsyncClient):
    global ACCESS_TOKEN, REFRESH_TOKEN
    response = await ac.get(
        "/admins/refresh",
        headers={"Authorization": f"Bearer {REFRESH_TOKEN}"},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "refresh_token" in response.json()

    ACCESS_TOKEN = response.json()["access_token"]
    REFRESH_TOKEN = response.json()["refresh_token"]


async def test_logout(ac: AsyncClient):
    response = await ac.get(
        "/admins/logout",
        headers={"Authorization": f"Bearer {ACCESS_TOKEN}"},
    )
    assert response.status_code == 200


async def test_refresh_token_after_logout(ac: AsyncClient):
    response = await ac.get(
        "/admins/refresh",
        headers={"Authorization": f"Bearer {REFRESH_TOKEN}"},
    )
    assert response.status_code == 400
    assert "Token invalid" in response.json()["detail"]
