#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : swagger_views.py
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from starlette.status import HTTP_401_UNAUTHORIZED

from conf import settings
from core.base_schemas import Token
from core.security import authenticate_user, create_access_token

router = APIRouter()


@router.post(
    "/swagger/login/",
    response_model=Token,
    tags=["swagger"],
    description="文档登录接口",
    include_in_schema=False,
)
async def swagger_login(
    user: OAuth2PasswordRequestForm = Depends(),
):
    auth_user = await authenticate_user(user.username, user.password)
    if not auth_user:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Invalid oauth",
        )
    access_token_expires = timedelta(hours=settings.ACCESS_TOKEN_EXPIRE_HOURS)
    access_token = create_access_token(
        data={"username": user.username, "role": auth_user.role, "uid": auth_user.id},
        expires_delta=access_token_expires,
    )
    return {
        "access_token": access_token,
        "token_type": "Bearer",
        "username": auth_user.username,
        "role": auth_user.role,
        "uid": auth_user.id,
    }
