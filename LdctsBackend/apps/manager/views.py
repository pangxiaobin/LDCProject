#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : views.py
from fastapi import APIRouter, Query, Depends

from core.security import verify_user_login
from .curd import DictServerDataModel
from .schema import DictServerDataOut
from core.base_response import resp_200


router = APIRouter()


@router.get(
    "/manager/dict",
    response_model=DictServerDataOut,
    description="字典服务缓存接口",
    dependencies=([Depends(verify_user_login)]),
)
async def get_data_dict(url_path: str = Query(description="字典服务中中的path")):
    data = await DictServerDataModel.get_dict_by_key(url_path)
    return resp_200(data=data)
