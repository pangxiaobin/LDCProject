#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : router.py

"""
register all router like django
Examples:
    import  my_api_router
    router = APIRouter()
    router.include_router(my_api_router)
"""
from fastapi import APIRouter, Depends

from apps.swagger_views import router as swagger_router
from apps.user.views import router as user_router
from apps.study.views import router as study_router
from apps.manager.views import router as manager_router
from core.security import swagger_oauth2_scheme

api_v1_router = APIRouter(
    dependencies=[
        Depends(swagger_oauth2_scheme),
    ],
)

api_v1_router.include_router(user_router, prefix="/api", tags=["user"])
api_v1_router.include_router(study_router, prefix="/api", tags=["study"])
api_v1_router.include_router(manager_router, prefix="/api", tags=["manager"])
api_v1_router.include_router(swagger_router, tags=["swagger"])


@api_v1_router.get("/", description="项目说明")
async def index():
    """
    说明
    """
    return "访问/swagger/docs/ 查看接口文档"
