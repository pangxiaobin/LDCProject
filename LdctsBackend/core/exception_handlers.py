#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : exceptions.py
from typing import Union

from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from starlette import status
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse

from common.log import logger
from conf import settings
from core.error_enums.error import ParamError
from core.error_enums.exception import ServerException
import traceback


async def system_error_handler(_: Request, exc: Exception):
    """
    系统错误异常
    :param _:
    :param exc:
    :return:
    """
    logger.error(exc.args)
    logger.error(traceback.format_exc())
    return JSONResponse(
        {"code": 9999, "msg": "系统错误 ，请联系管理员"},
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


async def http_error_handler(_: Request, exc: HTTPException):
    """
    http异常处理
    :param _:
    :param exc:
    :return:
    """

    return JSONResponse(
        {"code": exc.status_code, "msg": exc.detail, "data": exc.detail},
        status_code=exc.status_code,
        headers=exc.headers,
    )


async def custom_exception_handler(_: Request, exc: ServerException):
    """
    自定义 异常处理
    :param _:
    :param exc:
    :return:
    """
    logger.error(f"server exception: {exc.message}")
    return JSONResponse(
        {
            "code": exc.code,
            "msg": exc.message,
        },
        status_code=status.HTTP_200_OK,
    )


async def validate_error_handler(
    _: Request,
    exc: Union[RequestValidationError, ValidationError],
) -> JSONResponse:
    """
    参数校验错误处理
    :param _:
    :param exc:
    :return:
    """
    logger.error(f"request validation error {exc.errors()}")
    return JSONResponse(
        {
            "code": ParamError.code,
            "msg": exc.errors() if settings.DEBUG else ParamError.message,
        },
        status_code=status.HTTP_200_OK,
    )
