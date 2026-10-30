#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : schema.py
from typing import List, Optional, Union

from fastapi import Query
from pydantic import BaseModel, Field, field_validator
from tortoise.contrib.pydantic import pydantic_model_creator

from core.base_schemas import BaseListOut, ValidatorTime, BaseOut, Token
from models.base import User


class UserLoginRequest(BaseModel):
    username: str = Field(description="user name")
    password: str = Field(description="密码")


UserInDetail = pydantic_model_creator(User, name="UserInDb", exclude=("password",))


class UserDetail(UserInDetail, ValidatorTime):
    @field_validator("last_login", check_fields=False)
    @classmethod
    def format_last_login(cls, value) -> str:
        if not value:
            return ""
        if isinstance(value, str):
            return value
        return value.strftime("%Y-%m-%d %H:%M:%S")


class UserSimpleDetail(BaseModel):
    id: int
    username: str
    role: str


class UserSimpleList(BaseOut):
    data: List[UserSimpleDetail]


class UserInfo(BaseOut):
    data: UserDetail


class UserList(BaseListOut):
    data: List[UserDetail]


class UserRequestResetPassword(BaseModel):
    user_id: int = Field(description="用户id")
    new_password: str = Field(description="新密码")


UserCreate = pydantic_model_creator(
    User, name="UserCreate", exclude=("id", "create_time", "update_time", "last_login")
)


class UserUpdate(BaseModel):
    username: str = Field(description="用户名")
    is_active: bool = Field(description="是否激活")
    role: str = Field(description="角色")


class UserToken(BaseOut):
    data: Token
