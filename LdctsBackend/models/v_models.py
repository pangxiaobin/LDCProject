#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : v_models.py
from tortoise import Model, fields

from common.globals_enums import CheckStatusEnum


class V_Study(Model):
    study_instance_id = fields.CharField(max_length=256)
    patient_age = fields.CharField(max_length=6, null=True)
    patient_gender = fields.CharField(max_length=20, null=True)
    save_time = fields.CharField(max_length=30, null=True, description="保存时间")
    study_time = fields.CharField(max_length=128, null=True, description="检查时间")
    # study_ai_result = fields.JSONField(null=True, description="ai 结果")
    ai_status = fields.CharField(max_length=48, null=True, description="ai状态")

    check_status = fields.CharField(
        max_length=30,
        description=f"study审核状态: {[(enum.name, enum.value) for enum in CheckStatusEnum]}",
        null=True,
    )
    first_check_user_id = fields.IntField(null=True)
    first_check_user_username = fields.CharField(null=True, max_length=128)
    first_status = fields.CharField(null=True, max_length=128)
    last_check_user_id = fields.IntField(null=True)
    last_check_user_username = fields.CharField(null=True, max_length=128)
    last_status = fields.CharField(null=True, max_length=128)
    last_status_ai = fields.CharField(null=True, max_length=128)

    class Meta:
        table = "v_study"
        table_description = "study view"
