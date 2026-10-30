#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : curd.py
import datetime
from datetime import timedelta
from typing import List

from fastapi.encoders import jsonable_encoder
from tortoise.exceptions import DoesNotExist, MultipleObjectsReturned
from tortoise.queryset import QuerySet

from common.globals_enums import RoleEnum
from conf import settings
from core.error_enums.error import UserHasExist, UserNotExist, UserPasswordError
from core.security import create_access_token, get_password_hash, verify_password
from models.base import User

from .schema import *


class AuthenticationCRUD:
    """
    认证
    """

    @staticmethod
    async def login(user_req: UserLoginRequest) -> dict:
        try:
            user_obj = await User.get(username=user_req.username)
        except (DoesNotExist, MultipleObjectsReturned):
            raise UserNotExist

        if not verify_password(user_req.password, user_obj.password):
            raise UserPasswordError
        user_obj.last_login = datetime.datetime.now()
        await user_obj.save()
        access_token_expires = timedelta(hours=settings.ACCESS_TOKEN_EXPIRE_HOURS)
        access_token = create_access_token(
            data={
                "username": user_obj.username,
                "role": user_obj.role,
                "uid": user_obj.id,
            },
            expires_delta=access_token_expires,
        )

        username = user_obj.username
        return {
            "access_token": access_token,
            "token_type": "Bearer",
            "username": username,
            "role": user_obj.role,
            "uid": user_obj.id,
        }


class UserModel:
    """
    用户
    """

    @staticmethod
    async def get_user_list(
        page: int,
        page_size: int = 20,
        username: str = "",
        role: str = "",
        is_active: Union[bool, str] = "",
        is_all: Union[bool, str] = False,
    ) -> (QuerySet, int):
        """
        获取用户列表
        """
        offset = (page - 1) * page_size
        query_set = User.all()
        if username:
            query_set = query_set.filter(username__icontains=username)
        if str(is_all) in ["true", "1", "yes", "on"]:
            total = await query_set.count()
            data_list = await query_set.order_by("-id")
            return data_list, total
        if role:
            role_list = role.split(",")
            query_set = query_set.filter(role__in=role_list)
        if is_active != "":
            is_active = is_active.lower() in ["true", "1", "yes", "on"]
            query_set = query_set.filter(is_active=is_active)
        total = await query_set.count()
        data_list = await query_set.offset(offset).limit(page_size).order_by("-id")
        return data_list, total

    @staticmethod
    async def get_check_user_list(
        username: str = "", is_active: Union[bool, str] = ""
    ) -> list:
        query_set = User.all().filter(
            role__in=(RoleEnum.FIRST_AUDIT, RoleEnum.LAST_AUDIT)
        )
        if username:
            query_set = query_set.filter(username__icontains=username)
        if is_active != "":
            is_active = is_active.lower() in ["true", "1", "yes", "on"]
            query_set = query_set.filter(is_active=is_active)
        data = await query_set.values("id", "username", "role")
        return data

    @staticmethod
    async def get_user_by_id(user_id):
        try:
            user = await User.get(id=user_id)
        except (DoesNotExist, MultipleObjectsReturned):
            return None
        return user

    @staticmethod
    async def create_user(user: UserCreate):
        """
        新增
        """
        if await User.filter(username=user.username).exists():
            raise UserHasExist
        obj_in_data = jsonable_encoder(user)
        obj_in_data["password"] = get_password_hash(obj_in_data["password"])
        obj = User(**obj_in_data)
        await obj.save()

    @staticmethod
    async def reset_user_password(user_id: int, new_password: str) -> None:
        """
        修改密码
        """
        user = await UserModel.get_user_by_id(user_id)
        if not user:
            raise UserNotExist
        user.password = get_password_hash(new_password)
        await user.save()

    @staticmethod
    async def delete_user(user_id: int) -> None:
        """
        删除用户
        """
        user = await UserModel.get_user_by_id(user_id)
        if not user:
            raise UserNotExist
        user.is_active = False
        await user.save()

    @staticmethod
    async def update_user(user_id: int, user_obj: UserUpdate) -> None:
        """
        更新用户
        """
        await User.filter(id=user_id).update(**user_obj.model_dump(exclude_unset=True))
