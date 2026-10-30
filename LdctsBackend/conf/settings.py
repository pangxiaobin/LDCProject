#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : settings.py
import os
from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent
MEDIA_IDR = BASE_DIR / "media"
if not MEDIA_IDR.exists():
    MEDIA_IDR.mkdir(parents=True, exist_ok=True)


NIFTI_PNG_PATH: Path = Path("/var/www/png")

NIFTI_TEMP_DIR = BASE_DIR / "temp"
if not NIFTI_TEMP_DIR.exists():
    NIFTI_TEMP_DIR.mkdir(parents=True, exist_ok=True)


class Settings(BaseSettings):
    DEBUG: bool = Field(default=True, description="是否为开发模式")
    SERVER_NAME: str = Field(default="server", description="项目名")
    # swagger config
    TITLE: str = Field(default="Docs", description="swagger 文档标题")
    DESCRIPTION: str = Field(default="swagger docs ", description="swagger 文档 描述")
    DOCS_URL: str = Field(default="/swagger/docs", description="swagger 文档url")
    OPENAPI_URL: str = Field(
        default="/swagger/openapi.json", description="swagger OPENAPI_URL"
    )
    REDOC_URL: str = Field(default="/swagger/redoc", description="swagger REDOC_URL")

    BASE_DIR: Path = Field(default=BASE_DIR, description="项目基础路径")
    # jwt
    SECRET_KEY: str = Field(
        default="09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b8",
        description="秘钥值",
    )
    ALGORITHM: str = Field(default="HS256", description="加密算法")
    ACCESS_TOKEN_EXPIRE_HOURS: int = Field(default=24 * 7, description="token 过期时间")

    VERSIONS: str = Field(default="0.0.1", description="版本号")

    # 不需要进行登录验证的url
    # swagger 界面接口测试
    EXCLUDE_API_URL: tuple = (
        "/api/auth/login",
        "/api/swagger/",
        "/",
        "/api/studys/push",
    )
    EXCLUDE_API_RE_URL: tuple = (
        r"^.*/swagger/.*$",
        r"^.*/media/.*$",
        r"^/api/studys/audit/export.*$",
    )
    MEDIA_IDR: Path = MEDIA_IDR
    MEDIA_URL_PREFIX: str = Field(default="/media", description="媒体资源url前缀")
    # 日志
    LOG: dict = {"max_log_size": "20MB", "backup_count": 20}

    NIFTI_PNG_PATH_TEM: Path = MEDIA_IDR / "png"
    NIFTI_PNG_PATH: Path = NIFTI_PNG_PATH
    NIFTI_TEMP_DIR: Path = NIFTI_TEMP_DIR

    # third part url
    STUDY_DATA_URL: str = Field(
        default="http://123.56.82.224:8001/mock", description="获取影像数据的地址"
    )
    DICT_DARA_SERVER: str = Field(
        default="http://123.56.82.224:8000/", description="获取字典数据的服务地址"
    )
    BROKER_URL: str = Field(
        default="redis://127.0.0.1:6380/0", description="celery broker url"
    )
    BROKER_BACKEND: str = Field(
        default="redis://127.0.0.1:6380/0", description="celery broker backend"
    )

    model_config = SettingsConfigDict(env_file=".env")


@lru_cache
def get_settings():
    return Settings()


settings = get_settings()

if not settings.DEBUG:
    if not NIFTI_PNG_PATH.exists():
        NIFTI_PNG_PATH.mkdir(parents=True, exist_ok=True)
