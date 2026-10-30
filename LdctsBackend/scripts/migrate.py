#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : migrate.py

import asyncio
import sys
from pathlib import Path

from aerich import Command

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # isort:skip

from common.log import logger
from db.database import TORTOISE_ORM

BASE_DIR = Path(__file__).resolve().parent.parent

migration_path = f"{BASE_DIR}/migrations"
if not Path(migration_path).exists():
    # after build:
    BASE_DIR = Path(__file__).resolve().parent
    migration_path = f"{BASE_DIR}/migrations"

command = Command(tortoise_config=TORTOISE_ORM, app="base", location=migration_path)


async def migrate():
    await command.init()
    migrated = await command.upgrade(run_in_transaction=True)
    if not migrated:
        logger.warning("No upgrade items found")
    else:
        for version_file in migrated:
            logger.info(f"Success upgrade {version_file}")


if __name__ == "__main__":
    asyncio.run(migrate())
