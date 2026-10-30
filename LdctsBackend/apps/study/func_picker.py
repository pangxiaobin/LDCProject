#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : function_pick.py
import datetime

from common.globals_enums import CheckStatusEnum, RoleEnum
from core.error_enums.exception import FORBIDDENHTTPException, ServerException
from models.base import StudyAudit


async def func_er(token, study_id, front_status, **kwargs):
    if await StudyAudit.filter(study_id=study_id).exists():
        study_audit = await StudyAudit.filter(study_id=study_id).first()
        backend_status = study_audit.check_status
    else:
        backend_status = CheckStatusEnum.audit_not_audit
    en_msg = f"The operation is not supported when trying to {backend_status} to {front_status}"
    cn_msg = f"不支持该操作 {backend_status} 到 {front_status}"
    _StudyAuditUpdateError = ServerException(code=10008, cn_msg=cn_msg, en_msg=en_msg)
    raise _StudyAuditUpdateError


# 未审核-->初审中
async def func_01(token, study_id, front_status, **kwargs):
    role = token.role
    uid = token.uid
    if role == RoleEnum.FIRST_AUDIT:
        await StudyAudit.update_or_create(
            study_id=study_id,
            defaults={
                "first_check_user_id": uid,
                "check_status": front_status,
                "first_check_time": datetime.datetime.now(),
            },
        )
    else:
        raise FORBIDDENHTTPException()


# 未审核-->终审中
async def func_03(token, study_id, front_status, **kwargs):
    role = token.role
    uid = token.uid
    if role == RoleEnum.LAST_AUDIT:
        await StudyAudit.update_or_create(
            study_id=study_id,
            defaults={
                "last_check_user_id": uid,
                "check_status": front_status,
                "last_check_time": datetime.datetime.now(),
            },
        )
    else:
        raise FORBIDDENHTTPException()


# 初审中-->初审完成
async def func_12(token, study_id, front_status, **kwargs):
    role = token.role
    first_status = kwargs.get("status")
    first_report = kwargs.get("report")
    first_mark = kwargs.get("mark")
    if role == RoleEnum.FIRST_AUDIT:
        await StudyAudit.filter(
            study_id=study_id,
        ).update(
            check_status=front_status,
            first_status=first_status,
            first_mark=first_mark,
            first_report=first_report,
        )
    else:
        raise FORBIDDENHTTPException()


# 初审完成-->终审中
async def func_23(token, study_id, front_status, **kwargs):
    role = token.role
    uid = token.uid
    if role == RoleEnum.LAST_AUDIT:
        await StudyAudit.filter(
            study_id=study_id,
        ).update(check_status=front_status, last_check_user_id=uid)
    else:
        raise FORBIDDENHTTPException()


# 终审中 -->终审完成
async def func_34(token, study_id, front_status, **kwargs):
    role = token.role
    last_status_ai, last_status = kwargs.get("status").split(",")
    last_report = kwargs.get("report")
    last_mark = kwargs.get("mark")
    if role == RoleEnum.LAST_AUDIT:
        await StudyAudit.filter(
            study_id=study_id,
        ).update(
            check_status=front_status,
            last_status=last_status,
            last_status_ai=last_status_ai,
            last_mark=last_mark,
            last_report=last_report,
        )
    else:
        raise FORBIDDENHTTPException()


class Picker:
    func_array = [
        # 未审核0  初审中1   初审完成2  终审中3   终审完成4   数据库状态/前端请求状态
        [func_er, func_01, func_er, func_03, func_er],  # 未审核0
        [func_er, func_er, func_12, func_er, func_er],  # 初审中1
        [func_er, func_er, func_er, func_23, func_er],  # 初审完成2
        [func_er, func_er, func_er, func_er, func_34],  # 终审中3
        [func_er, func_er, func_er, func_er, func_er],  # 终审完成4
    ]

    @classmethod
    def get_func(cls, backend_status, front_status):
        return cls.func_array[CheckStatusEnum.index(backend_status)][
            CheckStatusEnum.index(front_status)
        ]
