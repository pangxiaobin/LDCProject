#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : schema.py
from typing import List, Optional, Union

from fastapi import Query
from pydantic import BaseModel, Field, field_validator
from tortoise.contrib.pydantic import pydantic_model_creator

from core.base_schemas import BaseListOut, ValidatorTime, BaseOut, Token, base_exclude
from models.base import DictServerData


DictServerDataDetail = pydantic_model_creator(
    DictServerData,
    name="DictServerDataDetail",
    exclude=base_exclude,
)


class DictServerDataOut(BaseOut):
    data: DictServerDataDetail
