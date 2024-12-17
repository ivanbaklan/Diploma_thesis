import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_get_main(client: AsyncClient):
    response = await client.get("/")
    assert response.status_code == 200


@pytest.mark.anyio
async def test_create_user(client: AsyncClient):
    data = {
        "username": "user",
        "email": "user@test.ru",
        "password": "1234",
        "confirm_password": "1234",
    }
    response = await client.post("user/register", data=data)
    assert response.status_code == 302
    data = {
        "username": "user",
        "email": "user@test.ru",
        "password": "1234",
        "confirm_password": "1234",
    }
    response = await client.post("user/register", data=data)
    assert response.status_code == 400
    data = {
        "username": "user",
        "email": "user@test.ru",
        "password": "12345",
        "confirm_password": "1234",
    }
    response = await client.post("user/register", data=data)
    assert response.status_code == 400
