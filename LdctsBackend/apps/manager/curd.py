#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : curd.py
from tortoise.exceptions import DoesNotExist

from core.error_enums.error import DataDictNotExist
from models.base import DictServerData
from .schema import DictServerDataDetail


class DictServerDataModel:
    @staticmethod
    async def get_dict_by_key(url_path: str) -> dict:
        try:
            data_obj = await DictServerData.get(url_path=url_path)
        except DoesNotExist:
            raise DataDictNotExist
        return DictServerDataDetail.model_dump(
            DictServerDataDetail.model_validate(data_obj, strict=True)
        )
