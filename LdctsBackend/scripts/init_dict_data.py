#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : init_dict_data.py

import asyncio
import sys
from pathlib import Path

from tortoise import Tortoise

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # isort:skip
from common.log import logger  # isort:skip
from db.database import do_stuff
from apps.study.utils import update_dict_data


async def main() -> None:
    logger.info("init connections")
    await do_stuff()
    logger.info("init dict data")
    await update_dict_data()
    await Tortoise.close_connections()


if __name__ == "__main__":
    asyncio.run(main())
