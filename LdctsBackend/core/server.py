#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : server.py

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException
from starlette.staticfiles import StaticFiles

from common.log import logger
from conf import settings
from core import events, exception_handlers
from core.error_enums.exception import ServerException
from core.router import api_v1_router


def create_app() -> FastAPI:
    """
    create app obj
    :return: FastAPI
    """
    app = FastAPI(
        debug=settings.DEBUG,
        title=settings.TITLE,
        description=settings.DESCRIPTION,
        docs_url=settings.DOCS_URL,
        openapi_url=settings.OPENAPI_URL,
        redoc_url=settings.REDOC_URL,
        openapi_tags=[
            {"name": "user", "description": "用户相关接口"},
        ],
    )
    # 日志文件
    logger.setup(settings.SERVER_NAME)

    # 事件监听
    app.add_event_handler("startup", events.startup(app))
    app.add_event_handler("shutdown", events.stopping(app))

    # register router
    register_router(app)
    register_middle(app)
    # 挂载静态文件
    app.mount(
        settings.MEDIA_URL_PREFIX,
        StaticFiles(directory=settings.MEDIA_IDR),
        name="media",
    )
    # 注册自定义异常
    register_handler_exception(app)

    return app


def register_router(app: FastAPI) -> None:
    """
    register router
    :param app:
    :return:
    """
    app.include_router(
        api_v1_router,
    )


def register_middle(app: FastAPI) -> None:
    """
    register middle
    :param app:
    :return:
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # 这里可以设置允许的源，例如："http://localhost:8080"
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def register_handler_exception(app: FastAPI) -> None:
    """
    注册异常
    :param app:
    :return:
    """
    app.add_exception_handler(Exception, exception_handlers.system_error_handler)
    app.add_exception_handler(HTTPException, exception_handlers.http_error_handler)
    app.add_exception_handler(
        ServerException, exception_handlers.custom_exception_handler
    )
    app.add_exception_handler(
        RequestValidationError, exception_handlers.validate_error_handler
    )
