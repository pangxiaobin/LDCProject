#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : security.py

from datetime import datetime, timedelta
from typing import Optional, Union

from fastapi import HTTPException
from fastapi.security import OAuth2PasswordBearer
from fastapi.security.utils import get_authorization_scheme_param
from jose import JWTError, jwt
from passlib.context import CryptContext
from starlette.requests import Request
from starlette.status import HTTP_401_UNAUTHORIZED
from tortoise.exceptions import DoesNotExist, MultipleObjectsReturned

from common.utils import check_re_match_url
from conf import settings
from models.base import RoleEnum, User

from .base_schemas import TokenData
from .error_enums.exception import AuthHTTPException, FORBIDDENHTTPException

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password) -> bool:
    """
    校验密码
    :param plain_password:
    :param hashed_password:
    :return:
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password) -> str:
    """
    获取hash密码
    :param password:
    :return:
    """
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    """
    创建jwt token
    :param data:
    :param expires_delta:
    :return:
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=7)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def parse_access_token(token: str) -> TokenData:
    """
    解析token
    :param token:
    :return:
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        username: str = payload.get("username")
        if username is None:
            raise AuthHTTPException()
        token_data = TokenData(**payload)
    except JWTError:
        raise AuthHTTPException()
    return token_data


async def authenticate_user(username: str, password: str) -> Union[bool, User]:
    """
    校验用户登录
    :param username:
    :param password:
    :return:
    """
    try:
        user = await User.get(username=username)
    except (DoesNotExist, MultipleObjectsReturned):
        return False
    if not verify_password(password, user.password):
        return False
    return user


class VerifyOAuthUserBearer:
    def __init__(self, role: list = []):
        self.role = role

    async def __call__(self, request: Request) -> Union[dict, TokenData]:
        authorization = request.headers.get("Authorization")
        scheme, param = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != "bearer":
            raise AuthHTTPException()
        token = parse_access_token(param)
        if self.role:
            if token.role not in self.role:
                raise FORBIDDENHTTPException()
        return token


# 验证登录的用户
verify_user_login = VerifyOAuthUserBearer()

# 验证必须是admin用户
verify_admin_user = VerifyOAuthUserBearer(role=[RoleEnum.ADMIN])

# 验证必须是审核员
verify_audit_user = VerifyOAuthUserBearer(
    role=[RoleEnum.FIRST_AUDIT, RoleEnum.LAST_AUDIT]
)


class SwaggerOAuth2PasswordBearer(OAuth2PasswordBearer):
    async def __call__(self, request: Request) -> Optional[str]:
        url_path = request.url.path
        if url_path in settings.EXCLUDE_API_URL or check_re_match_url(
            url_path, settings.EXCLUDE_API_RE_URL
        ):
            return
        authorization = request.headers.get("Authorization")
        scheme, token = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != "bearer":
            if self.auto_error:
                raise HTTPException(
                    status_code=HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            else:
                return None
        return token


swagger_oauth2_scheme = SwaggerOAuth2PasswordBearer(tokenUrl="/swagger/login/")
