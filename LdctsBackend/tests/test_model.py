#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : test_model.py
import json

import pytest
from tortoise.exceptions import DoesNotExist
from core.security import get_password_hash

from models.base import *


@pytest.mark.anyio
async def test_user_crud():
    # 创建用户
    user = await User.create(
        username="test user",
        password=get_password_hash("password123"),
        role=RoleEnum.NORMAL,
    )

    # 查询用户是否存在
    assert await User.exists(username="test user")

    # 更新用户信息
    await User.filter(username="test user").update(role="1")
    updated_user = await User.get(username="test user")
    assert updated_user.role == "1"

    # 删除用户
    await User.filter(username="test user").delete()

    # 确认用户已被删除
    with pytest.raises(DoesNotExist):
        await User.get(username="test user")


@pytest.mark.anyio
async def test_study_curd():
    study = await Study.create(
        study_instance_id="1234567890",
        patient_age="18",
        patient_gender="male",
        save_time="2023-01-01 00:00:00",
        study_time="2023-01-01 00:00:00",
        study_ai_result={
            "classifier": {
                "classifer.stent": "classifier_stent_invisible",
                "classifier.pacemaker": "classifier_pacemaker_lesion_invisible",
                "classifier.chestwall": "classifier_chestvall_lesion_invisible",
                "classifier.vertebrae": "classifier_vertebrae_lesion_invisible",
                "classifier.mediastinum": "classifier_mediastinum_lesion_invisible",
            }
        },
        ai_status="airesult_success",
    )
    assert await Study.exists(study_instance_id="1234567890")

    await Study.filter(study_instance_id="1234567890").update(ai_status="airesult_fail")
    update_study = await Study.get(study_instance_id="1234567890")
    assert update_study.ai_status == "airesult_fail"

    study = await Study.filter(study_instance_id="1234567890").first()
    assert study.study_ai_result.get("classifier") == {
        "classifer.stent": "classifier_stent_invisible",
        "classifier.pacemaker": "classifier_pacemaker_lesion_invisible",
        "classifier.chestwall": "classifier_chestvall_lesion_invisible",
        "classifier.vertebrae": "classifier_vertebrae_lesion_invisible",
        "classifier.mediastinum": "classifier_mediastinum_lesion_invisible",
    }
    await Study.filter(study_instance_id="1234567890").delete()
    # 确认已被删除
    with pytest.raises(DoesNotExist):
        await Study.get(study_instance_id="1234567890")
