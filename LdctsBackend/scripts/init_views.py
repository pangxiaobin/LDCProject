#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : init_views.py
import asyncio
import sys
from pathlib import Path

from tortoise import Tortoise

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # isort:skip

from common.log import logger
from db.database import do_stuff


async def check_view_exist(view_name: str) -> bool:
    """
    判决视图是否存在
    """
    await do_stuff()
    client = Tortoise.get_connection("default")
    if client.capabilities.dialect == "sqlite":
        check_view_query = (
            f"SELECT name FROM sqlite_master WHERE type='view' AND name='{view_name}';"
        )
    else:
        check_view_query = f"""
        SELECT TABLE_NAME
        FROM INFORMATION_SCHEMA.VIEWS
        WHERE TABLE_SCHEMA = 'ldcts_db' AND  TABLE_NAME = '{view_name}';
        """
    exist, _ = await client.execute_query(check_view_query)
    await client.close()
    return bool(exist)


async def drop_view(view_name: str):
    """
    判决视图是否存在
    """
    await do_stuff()
    client = Tortoise.get_connection("default")
    drop_view_query = f"DROP VIEW {view_name}"
    await client.execute_script(drop_view_query)
    await client.close()


async def create_study_view(is_drop=False):
    """
    创建study 视图表
    """
    view_name = "v_study"
    exist = await check_view_exist(view_name)
    if exist and not is_drop:
        logger.info(f"The {view_name} already exists!")
        return
    if exist and is_drop:
        await drop_view(view_name)
    await do_stuff()
    client = Tortoise.get_connection("default")
    sql_script = f"""
        CREATE VIEW {view_name} AS
        SELECT st.id, st.study_instance_id, st.patient_age, st.patient_gender, st.save_time, st.study_time,
        st.ai_status,
        saa.first_check_user_id,
        saa.first_check_user_username,
        saa.first_status,
        saa.last_check_user_username,
        saa.last_check_user_id,
        saa.last_status,
        saa.last_status_ai,
        saa.check_status
        FROM study st
        LEFT JOIN
            (SELECT sa.*, u1.username AS first_check_user_username, u2.username AS last_check_user_username
            FROM studyaudit sa
            LEFT JOIN user u1 ON sa.first_check_user_id = u1.id
            LEFT JOIN user u2 ON sa.last_check_user_id = u2.id) AS saa
        ON st.id = saa.study_id;
         """
    await client.execute_script(sql_script)
    logger.info(f"Create {view_name} success!")
    await client.close()


async def run():
    await create_study_view(is_drop=True)


if __name__ == "__main__":
    asyncio.run(run())
