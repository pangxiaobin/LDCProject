#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : exception.py
from typing import Any, Dict, Optional

from fastapi import HTTPException
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN


class Language:
    """
    语言
    """

    cn = "cn"
    en = "en"


class ServerException(Exception):
    """
    自定义错误
    """

    def __init__(self, code=9999, cn_msg="未知错误", en_msg="Unknown exception occurred!"):
        self.__code = code
        self.__cn_msg = cn_msg
        self.__en_msg = en_msg
        super().__init__(self, cn_msg)

    def __str__(self):
        return self.__cn_msg

    @property
    def code(self):
        return self.__code

    @property
    def message(self):
        return self.__cn_msg

    def get_message(self, lang=Language.cn):
        if lang == Language.cn:
            return self.__cn_msg
        else:
            return self.__en_msg


class AuthHTTPException(HTTPException):
    """
    未登录异常
    """

    def __init__(
        self,
        status_code: int = HTTP_401_UNAUTHORIZED,
        detail: Any = "Not authenticated",
        headers: Optional[Dict[str, str]] = {"WWW-Authenticate": "Bearer"},
    ) -> None:
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class FORBIDDENHTTPException(HTTPException):
    """
    没有权限
    """

    def __init__(
        self,
        status_code: int = HTTP_403_FORBIDDEN,
        detail: Any = "forbidden error",
        headers: Optional[Dict[str, str]] = {},
    ) -> None:
        super().__init__(status_code=status_code, detail=detail, headers=headers)
