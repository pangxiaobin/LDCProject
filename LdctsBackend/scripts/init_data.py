#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : init_data.py

import asyncio
import sys
from pathlib import Path

from tortoise import Tortoise

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # isort:skip

from common.log import logger  # isort:skip
from common.globals_enums import RoleEnum  # isort:skip
from core.security import get_password_hash  # isort:skip
from db.database import do_stuff  # isort:skip
from models.base import User  # isort:skip


async def create_admin_account():
    """
    初始化 管理员账号
    :return:
    """
    admin = await User.exists(username="ldcts")
    if not admin:
        await User.create(
            username="ldcts",
            role=RoleEnum.ADMIN,
            password=get_password_hash("ldcts"),
        )


async def main() -> None:
    logger.info("init database")
    await do_stuff()
    logger.info("init admin account")
    await create_admin_account()
    await Tortoise.close_connections()


if __name__ == "__main__":
    asyncio.run(main())
