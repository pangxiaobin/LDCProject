#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : views.py
from typing import Optional, Union

from fastapi import APIRouter, Depends, Query

from core.base_response import resp_200
from core.base_schemas import BaseOut, Token
from core.security import verify_admin_user, verify_user_login

from .curd import AuthenticationCRUD, UserModel
from .schema import (
    UserCreate,
    UserDetail,
    UserList,
    UserLoginRequest,
    UserRequestResetPassword,
    UserUpdate,
    UserInfo,
    UserToken,
    UserSimpleList,
    UserSimpleDetail,
)

router = APIRouter()


@router.post("/auth/login", response_model=UserToken, description="登录")
async def user_login(user: UserLoginRequest):
    """
    登录
    """
    token = await AuthenticationCRUD.login(user)
    return resp_200(data=token)


@router.get(
    "/users",
    response_model=UserList,
    description="用户列表",
    dependencies=[Depends(verify_admin_user)],
)
async def user_list(
    page: int = Query(default=1, description="页码"),
    page_size: int = Query(default=20, description="页码大小"),
    role: str = Query(default="", description="角色,多角色用','隔开"),
    username: str = Query(default="", description="用户名"),
    is_active: Union[bool, str] = Query(default="", description="状态"),
    is_all: Union[bool, str] = Query(default=False, description="是否获取全部"),
):
    query_set, total = await UserModel.get_user_list(
        page,
        page_size=page_size,
        username=username,
        role=role,
        is_active=is_active,
        is_all=is_all,
    )
    return resp_200(
        data=[UserDetail.model_validate(user, strict=False) for user in query_set],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/users/checks",
    response_model=UserSimpleList,
    description="用户审核员列表",
    dependencies=[Depends(verify_user_login)],
)
async def user_list(
    username: str = Query(default="", description="用户名"),
    is_active: Union[bool, str] = Query(default="", description="状态"),
):
    query_set = await UserModel.get_check_user_list(
        username=username, is_active=is_active
    )
    return resp_200(
        data=[
            UserSimpleDetail.model_validate(user, strict=False) for user in query_set
        ],
    )


@router.post(
    "/users",
    response_model=BaseOut,
    description="新增",
    dependencies=[Depends(verify_admin_user)],
)
async def user_create(user: UserCreate):
    await UserModel.create_user(user)
    return resp_200()


@router.put(
    "/users/reset_password",
    response_model=BaseOut,
    description="修改密码",
    dependencies=[Depends(verify_admin_user)],
)
async def user_reset_password(user_req: UserRequestResetPassword):
    await UserModel.reset_user_password(user_req.user_id, user_req.new_password)
    return resp_200()


@router.delete(
    "/users/{user_id}",
    response_model=BaseOut,
    description="删除",
    dependencies=[Depends(verify_admin_user)],
)
async def user_delete(user_id):
    await UserModel.delete_user(user_id)
    return resp_200()


@router.put(
    "/users/{user_id}",
    response_model=BaseOut,
    description="修改",
    dependencies=[Depends(verify_admin_user)],
)
async def user_update(user_id, user_obj: UserUpdate):
    await UserModel.update_user(user_id, user_obj)
    return resp_200()


@router.get("/users/info", response_model=UserInfo, description="用户信息")
async def user_info(token=Depends(verify_user_login)):
    uid = token.uid
    user = await UserModel.get_user_by_id(uid)
    return resp_200(data=UserDetail.model_validate(user))
