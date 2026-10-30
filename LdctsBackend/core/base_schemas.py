#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : base_schemas.py

from typing import List, Union

from fastapi import Query
from pydantic import BaseModel, Field, field_validator, validator


class BaseOut(BaseModel):
    code: int = 200
    msg: str


class Token(BaseModel):
    access_token: str
    token_type: str
    username: str
    role: str
    uid: int


class BaseListOut(BaseOut):
    total: int
    page: int = Query(1)
    page_size: int = Query(20)


class BaseMultDelete(BaseModel):
    ids: List[int] = []


class TokenData(BaseModel):
    username: Union[str, None] = None
    role: Union[str, None] = None
    uid: Union[int, None] = None


class ValidatorTime:
    """
    校验和序列化时间
    """

    @field_validator("create_time", "update_time", check_fields=False)
    @classmethod
    def format_time(cls, value) -> str:
        if isinstance(value, str):
            return value
        return value.strftime("%Y-%m-%d %H:%M:%S")


base_exclude = ("id", "create_time", "update_time")
