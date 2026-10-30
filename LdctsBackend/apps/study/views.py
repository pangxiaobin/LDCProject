#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : views.py
import io
import json as _json
import time

from fastapi import APIRouter, Query, BackgroundTasks, Depends
from fastapi.responses import StreamingResponse
from starlette.responses import JSONResponse

from core.base_response import resp_200
from typing import Union
from core.base_schemas import BaseOut, TokenData
from core.error_enums.error import RequestThirdPartyError
from core.security import verify_user_login, verify_audit_user, verify_admin_user
from workers.tasks import save_study_task
from .curd import (
    StudyModel,
    SeriesModel,
    StudyAuditModel,
    SeriesAuditLogModel,
    SeriesQualityControlModel,
)
from .schema import *
from aiohttp import ClientSession
from conf.settings import settings
from urllib.parse import quote

from .utils import save_study, background_save_study

router = APIRouter()


@router.post("/studys/push", response_model=BaseOut, description="推送")
async def study_push(item: StudyPush, background_tasks: BackgroundTasks):
    # 使用celery 异步任务
    save_study_task.delay(item.data)
    # background_tasks.add_task(save_study, item.data)
    return resp_200()


@router.get("/studys", response_model=StudyList, description="推送")
async def study_list(
    page: int = Query(default=1, description="页码"),
    page_size: int = Query(default=20, description="页码大小"),
    ai_status: Union[str, None] = Query(default=None, description="ai状态"),
    check_status: Union[str, None] = Query(default=None, description="审核状态"),
    study_instance_id: Union[str, None] = Query(default=None, description="检查号"),
    user_id: Union[int, None, str] = Query(default=None, description="审核用户id"),
):
    query_set, total = await StudyModel.get_study_list(
        page,
        page_size=page_size,
        ai_status=ai_status,
        check_status=check_status,
        study_instance_id=study_instance_id,
        user_id=user_id,
    )

    return resp_200(
        data=[StudyDetail.model_validate(study, strict=False) for study in query_set],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/studys/pull", response_model=BaseOut, description="拉取")
async def study_pull(background_tasks: BackgroundTasks):
    async with ClientSession() as session:
        async with session.get(settings.STUDY_DATA_URL) as resp:
            if resp.status != 200:
                raise RequestThirdPartyError
            data = await resp.json()
            detail = data.get("detail")
            background_tasks.add_task(background_save_study, detail)
    return resp_200()


@router.get("/studys/series", response_model=SeriesListInfo, description="影像列表")
async def study_series_list(
    study_id: int = Query(description="study.id"),
    token: TokenData = Depends(verify_user_login),
):
    role = token.role
    data = await SeriesModel.get_series_by_study_id(study_id, role)
    return resp_200(data=data)


@router.get(
    "/studys/serier/{series_id}",
    response_model=SeriesAnnoInfoOut,
    description="ai和标注信息",
)
async def study_series_annotion(
    series_id: int,
    token: TokenData = Depends(verify_user_login),
):
    data = await SeriesModel.get_series_anno_by_series_id(series_id)
    return resp_200(
        data=SeriesAnnoInfo.model_dump(
            SeriesAnnoInfo.model_validate(data, strict=False)
        )
    )


@router.post("/studys/audit", response_model=BaseOut, description="新增审核记录")
async def study_audit_create(
    audit: StudyAuditCreate, token: TokenData = Depends(verify_audit_user)
):
    await StudyAuditModel.create_study_audit(audit, token)
    return resp_200()


@router.post("/studys/upsert", response_model=BaseOut, description="提交审核")
async def study_audit_upsert(
    audit: StudyAuditUpdate, token: TokenData = Depends(verify_audit_user)
):
    await StudyAuditModel.upsert_study_audit(audit, token)
    return resp_200()


@router.post("/studys/classifier", response_model=BaseOut, description="保存classifier")
async def study_audit_update_classifier(
    audit: StudyAuditClassifierUpdate, token: TokenData = Depends(verify_audit_user)
):
    await StudyAuditModel.audit_update_classifier(audit, token)
    return resp_200()


@router.post("/studys/series/audit", response_model=BaseOut, description="保存ai标注和新增标注")
async def study_series_audit(
    series_audit: SeriesAuditLogCreate, token: TokenData = Depends(verify_audit_user)
):
    await SeriesAuditLogModel.series_audit_create(series_audit, token)
    return resp_200()


@router.get(
    "/studys/audit/export",
    response_class=StreamingResponse,
    description="数据导出",
)
async def study_audit_export(
    study_id: Union[int, None] = Query(default=None, description="系统中的study id"),
    patient_studyid: Union[str, None] = Query(
        default=None, description="patient.studyid"
    ),
):
    result = await StudyAuditModel.study_audit_export(
        study_id=study_id, patient_studyid=patient_studyid
    )
    json_str = _json.dumps(result)
    bytes_io = io.BytesIO(bytes(json_str, encoding="utf-8"))

    # StreamingResponse 将数据流作为响应返回
    response = StreamingResponse(bytes_io, media_type="application/octet-stream")
    file_name = f"{result.get('patient.studyid')}_study_id_{study_id}.json"
    encoded_name = quote(file_name)  # URL encode the file name

    response.headers[
        "Content-Disposition"
    ] = f"attachment; filename*=UTF-8''{encoded_name}"
    return response


@router.post(
    "/studys/delete",
    response_model=BaseOut,
    description="删除study",
    dependencies=([Depends(verify_admin_user)]),
)
async def study_delete(study_in: StudyDelete):
    await StudyModel.study_delete(study_in)
    return resp_200()


@router.post(
    "/studys/series/{series_id}/quality_control",
    response_model=BaseOut,
    description="序列质控新增或者更新",
    dependencies=([Depends(verify_audit_user)]),
)
async def series_quality_control_create_or_update(
    series_id: int,
    quality_control_in: SeriesQualityControlCreate,
):
    await SeriesQualityControlModel.series_quality_control_create_or_update(
        series_id, quality_control_in
    )
    return resp_200()
