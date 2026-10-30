#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : events.py
from typing import Callable

from fastapi import FastAPI
from tortoise import Tortoise

from common.log import logger
from db.database import register_tortoise_db


def startup(app: FastAPI) -> Callable:
    """
    FastApi 启动完成事件
    :param app: FastAPI
    :return: start_app
    """

    async def app_start() -> None:
        # APP启动完成后触发
        logger.info("server 已启动")
        # 注册数据库
        logger.info("register db")
        await register_tortoise_db(app)

    return app_start


def stopping(app: FastAPI) -> Callable:
    """
    FastApi 停止事件
    :param app: FastAPI
    :return: stop_app
    """

    async def stop_app() -> None:
        # APP停止时触发
        logger.info("server已停止")
        await Tortoise.close_connections()

    return stop_app
