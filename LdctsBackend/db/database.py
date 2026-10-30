#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : database.py
from tortoise import Tortoise
from tortoise.contrib.fastapi import register_tortoise

from conf.settings import settings

"""
DATABASE : support sqlite+aiosqlite, mysql+asyncmy, postgresql+asyncpg
mysql：
DATABASE = {
        "DB_TYPE": "mysql",
        "HOST":"127.0.0.1",
        "NAME": "db_name",
        "PASSWORD":"db_password",
        "PORT":"3306",
        "USER": "db_user"
}
"""
# DATABASE = {
#     "DB_TYPE": "sqlite",
#     "NAME": BASE_DIR
#             / (os.getenv("TEST_DATABASE") if os.getenv("TEST_DATABASE") else "db.sqlite3"),
# }

if settings.DEBUG:
    DATABASE = {
        "DB_TYPE": "mysql",
        "HOST": "127.0.0.1",
        "NAME": "ldcts_db",
        "PASSWORD": "123456",
        "PORT": "3306",
        "USER": "root",
    }
else:
    DATABASE = {
        "DB_TYPE": "mysql",
        "HOST": "mysql-db",
        "NAME": "ldcts_db",
        "PASSWORD": "c409b71ceb0b4711ad9c20df1b49806f",
        "PORT": "3307",
        "USER": "ldcts",
    }


def get_db_url() -> str:
    """
    获取数据库连接的url
    https://tortoise.github.io/databases.html?h=wal#tortoise.Tortoise.generate_schemas-parameters
    :return:
    """
    _data_base = DATABASE
    _db_type = _data_base.get("DB_TYPE")
    if _db_type == "sqlite":
        sqlite_name = _data_base["NAME"]
        url = f"sqlite://{sqlite_name}"
    elif _db_type == "mysql":
        url = f'mysql://{_data_base["USER"]}:{_data_base["PASSWORD"]}@{_data_base["HOST"]}/{_data_base["NAME"]}'
    elif _db_type == "postgresql":
        url = f'postgres://{_data_base["USER"]}:{_data_base["PASSWORD"]}@{_data_base["HOST"]}:{_data_base["PORT"]}/{_data_base["NAME"]}'
    else:
        raise Exception(f"Not support the {_db_type}")
    return url


TORTOISE_ORM = {
    "connections": {"default": get_db_url()},
    "apps": {
        "base": {
            "models": ["models.base", "aerich.models", "models.v_models"],
            "default_connection": "default",
        },
    },
    "use_tz": False,
    "timezone": "Asia/Shanghai",
}


TORTOISE_ORM_MIGRATE = {
    "connections": {"default": get_db_url()},
    "apps": {
        "base": {
            "models": ["models.base", "aerich.models"],
            "default_connection": "default",
        },
    },
    "use_tz": False,
    "timezone": "Asia/Shanghai",
}


async def register_tortoise_db(app):
    """
    配置Tortoise-ORM连接
    :param app:
    :return:
    """
    register_tortoise(app, config=TORTOISE_ORM)


async def do_stuff():
    """
    当需要单独脚本使用orm时，需要执行这个初始化
    :return:
    """
    await Tortoise.init(config=TORTOISE_ORM)
