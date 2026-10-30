#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : schema.py
from pydantic import BaseModel, json, Field
from typing import Dict, List, Union

from common.globals_enums import CheckStatusEnum
from core.base_schemas import BaseListOut, BaseOut, base_exclude
from models.v_models import V_Study
from models.base import Series, SeriesAuditLog, SeriesQualityControl

from tortoise.contrib.pydantic import pydantic_model_creator


class StudyPush(BaseModel):
    data: Dict = Field(description="提交的数据")


StudyDetail = pydantic_model_creator(
    V_Study,
    name="StudyDetail",
)


class StudyList(BaseListOut):
    data: List[StudyDetail]


SeriesDetail = pydantic_model_creator(
    Series, name="SeriesDetail", exclude=("create_time",), computed=("series_path",)
)


class SeriesInfo(BaseModel):
    study_id: int
    series: List[SeriesDetail]
    study_instance_id: str
    patient_age: Union[str, None]
    patient_gender: Union[str, None]
    ai_classifier: Union[list[dict], None]
    first_classifier: Union[list[dict], None]
    last_classifier: Union[list[dict], None]
    ai_report: Union[dict, None]
    first_status: Union[str, None]
    first_mark: Union[str, None]
    last_status: Union[str, None]
    last_status_ai: Union[str, None]
    last_mark: Union[str, None]


class SeriesListInfo(BaseOut):
    data: SeriesInfo


SeriesQualityControlDetail = pydantic_model_creator(
    SeriesQualityControl,
    name="SeriesQualityControlDetail",
    exclude=("create_time", "id"),
)

SeriesQualityControlCreate = pydantic_model_creator(
    SeriesQualityControl,
    name="SeriesQualityControlCreate",
    exclude=("create_time", "id"),
)


class SeriesAnnoInfo(BaseModel):
    ai_lesion_series: Union[list[dict], None]
    id: int
    series_filename: str
    first_ai_audit: Union[list[dict], None]
    first_user_audit: Union[list[dict], None]
    last_ai_audit: Union[list[dict], None]
    last_user_audit: Union[list[dict], None]
    quality_control: Union[SeriesQualityControlDetail, None]


class SeriesAnnoInfoOut(BaseOut):
    data: SeriesAnnoInfo


class StudyAuditCreate(BaseModel):
    study_id: int = Field(description="study.id")
    check_status: str = Field(
        description=f"study审核状态: {[(enum.name, enum.value) for enum in CheckStatusEnum]}"
    )


class StudyAuditUpdate(BaseModel):
    study_id: int = Field(description="study.id")
    check_status: str = Field(
        description=f"study审核状态: {[(enum.name, enum.value) for enum in CheckStatusEnum]}"
    )
    status: str = Field(description="用户审核状态")
    mark: Union[str, None] = Field(description="备注", default="")
    report: Union[dict, None] = Field(description="报告", default=None)


class StudyAuditClassifierUpdate(BaseModel):
    study_id: int = Field(description="study.id")
    classifier: Union[str, dict, list] = Field(
        default="", description="用户保存的classifier"
    )


class SeriesAuditLogCreate(BaseModel):
    series_id: int = Field(description="series.id")
    ai_audit: Union[dict, None, list] = Field(default=None, description="ai结果")
    user_audit: Union[dict, None, list] = Field(default=None, description="用户标注结果")


class StudyDelete(BaseModel):
    study_ids: List[int] = Field(description="study.id")
