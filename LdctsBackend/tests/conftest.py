#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : conftest.py
import pytest
from httpx import AsyncClient
from tortoise import Tortoise

from models.base import *
from core.server import create_app
from core.security import get_password_hash

DB_URL = "sqlite://:memory:"
admin_username, admin_password = ["ldcts", "ldcts"]
test_username, test_password = ["test_user", "test_password"]

# Configure Tortoise ORM


# 参考文档
# https://stackoverflow.com/questions/65716897/testing-in-fastapi-using-tortoise-orm/69055243
# https://github.com/waketzheng/fastapi-tortoise-pytest-demo.git


"""

pytest 中fixture的score几种类型说明
在 pytest 中，fixture 的 scope 参数可以用来控制 fixture 的作用范围。scope 参数有四种类型，分别是：
function：每个测试函数都会调用一次 fixture，即每个测试函数都会创建一个新的 fixture 实例。这是默认的 scope 类型。
class：每个测试类中的所有测试方法共享同一个 fixture 实例。在测试类中的第一个测试方法调用 fixture 时，会创建一个新的 fixture 实例，然后该实例会在整个测试类中的所有测试方法中共享。
module：每个测试模块中的所有测试方法共享同一个 fixture 实例。在测试模块中的第一个测试方法调用 fixture 时，会创建一个新的 fixture 实例，然后该实例会在整个测试模块中的所有测试方法中共享。
session：整个测试会话中的所有测试方法共享同一个 fixture 实例。在测试会话开始时调用 fixture 时，会创建一个新的 fixture 实例，然后该实例会在整个测试会话中的所有测试方法中共享。

"""


async def init_db(db_url, create_db: bool = False, schemas: bool = False) -> None:
    """Initial database connection"""

    TORTOISE_ORM = {
        "connections": {"default": db_url},
        "apps": {
            "base": {
                "models": ["models.base"],
                "default_connection": "default",
            },
        },
        "use_tz": False,
        "timezone": "Asia/Shanghai",
    }
    await Tortoise.init(
        config=TORTOISE_ORM,
        _create_db=create_db,
    )
    if create_db:
        print(f"Database created! {db_url}")
    if schemas:
        await Tortoise.generate_schemas()
        print("Success to generate schemas")


async def init(db_url: str = DB_URL):
    await init_db(db_url, True, True)


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session")
async def client():
    async with AsyncClient(app=create_app(), base_url="http://test") as client:
        print("Client is ready")
        yield client


@pytest.fixture(scope="session")
async def client_with_admin_token(client: AsyncClient):
    data = {"username": admin_username, "password": admin_password}
    response = await client.post("/api/auth/login", json=data)
    token_type = response.json().get("data").get("token_type")
    access_token = response.json().get("data").get("access_token")
    async with AsyncClient(
        app=create_app(),
        base_url="http://test",
        headers={"Authorization": f"{token_type} {access_token}"},
    ) as admin_client:
        yield admin_client


@pytest.fixture(scope="session")
async def client_with_norm_token(client: AsyncClient):
    """
    客户端
    :param client:
    :return:
    """
    data = {"username": test_username, "password": test_password}
    response = await client.post("/api/auth/login", json=data)
    token_type = response.json().get("data").get("token_type")
    access_token = response.json().get("data").get("access_token")
    async with AsyncClient(
        app=create_app(),
        base_url="http://test",
        headers={"Authorization": f"{token_type} {access_token}"},
    ) as norm_client:
        yield norm_client


async def init_sql():
    # 插入管理员账号
    await User.create(
        username=admin_username,
        password=get_password_hash(admin_password),
        role=RoleEnum.ADMIN,
    )
    await User.create(
        username=test_username,
        password=get_password_hash(test_password),
        role=RoleEnum.NORMAL,
    )


@pytest.fixture(scope="session", autouse=True)
async def initialize_tests():
    """
    初始化
    :return:
    """
    print("init db")
    await init()
    await init_sql()
    yield
    await Tortoise._drop_databases()
    print("cleanup db")
