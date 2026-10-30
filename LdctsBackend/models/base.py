#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : models.py
from datetime import datetime
from typing import Union

from tortoise import Model, fields

from common.globals_enums import (
    RoleEnum,
    CheckStatusEnum,
    FirstUserCheckStatus,
    LastUserCheckStatus,
    BreathArtifactEnum,
    MetalArtifactEnum,
    HeartArtifactEnum,
    PositionEnum,
    ImageQualityEnum,
    ImageIntegrityEnum,
    SpecialtyEnum,
)


class BaseCreateModel(Model):
    id = fields.BigIntField(pk=True)
    create_time: Union[str, datetime] = fields.DatetimeField(
        auto_now_add=True, description="创建时间"
    )

    class Meta:
        abstract = True


class BaseUpsertModel(BaseCreateModel):
    update_time: Union[str, datetime] = fields.DatetimeField(
        auto_now=True, description="更新时间"
    )

    class Meta:
        abstract = True


class User(BaseUpsertModel):
    username = fields.CharField(
        max_length=32, description="账号", unique=True, index=True
    )
    password = fields.CharField(max_length=128, description="密码")
    last_login: Union[str, datetime, None] = fields.DatetimeField(
        null=True, description="最近登录时间"
    )
    is_active = fields.BooleanField(default=True, description="状态")
    role = fields.CharEnumField(
        RoleEnum,
        default=RoleEnum.NORMAL,
        description=f"角色 {' '.join(['--'.join([str(enum.name), str(enum.value)]) for enum in RoleEnum])}",
    )

    class Meta:
        table_description = "用户"
        table = "user"


class Study(BaseUpsertModel):
    study_instance_id = fields.CharField(max_length=256, unique=True, index=True)
    patient_age = fields.CharField(max_length=6, null=True)
    patient_gender = fields.CharField(max_length=20, null=True)
    save_time = fields.CharField(max_length=30, null=True, description="保存时间")
    study_time = fields.CharField(max_length=128, null=True, description="检查时间")
    study_ai_result = fields.JSONField(null=True, description="ai 结果")
    ai_status = fields.CharField(max_length=48, null=True, description="ai状态")
    series: fields.ReverseRelation["Series"]


class Series(BaseCreateModel):
    study: fields.ForeignKeyRelation[Study] = fields.ForeignKeyField(
        "base.Study", related_name="series"
    )
    series_filename = fields.CharField(max_length=128, index=True, unique=True)
    recon = fields.CharField(null=True, max_length=64, description="序列的重建方式")
    breath_artifact = fields.CharField(
        null=True, max_length=128, blank=True, description="序列是否有呼吸伪影"
    )
    instance_num = fields.IntField(description="影像数据量")
    image_orientation_patient = fields.CharField(max_length=64)
    image_position_patient = fields.CharField(max_length=64)
    pixel_spacing = fields.CharField(max_length=64)
    nifti_size = fields.JSONField(null=True, description="影像大小x,y,x")
    series_quality_control: fields.ReverseRelation["SeriesQualityControl"]

    def series_path(self) -> str:
        """
        Returns the best name
        """
        return (
            f"/png/{self.series_filename.replace('.', '_')}"
            if self.series_filename
            else ""
        )

    class PydanticMeta:
        computed = ["series_path"]


class SeriesQualityControl(BaseCreateModel):
    series: fields.OneToOneRelation[Series] = fields.OneToOneField(
        "base.Series", related_name="series_quality_control"
    )
    breath_artifact = fields.CharField(
        max_length=40,
        default="breath_artifact_not_found",
        description=f"呼吸伪影 {' '.join(['--'.join([str(enum.name), str(BreathArtifactEnum.get_enum_values(enum.value))]) for enum in BreathArtifactEnum])}",
    )
    metal_artifact = fields.CharField(
        max_length=40,
        default="metal_artifact_not_found",
        description=f"金属伪影 {' '.join(['--'.join([str(enum.name), str(MetalArtifactEnum.get_enum_values(enum.value))]) for enum in MetalArtifactEnum])}",
    )
    heart_artifact = fields.CharField(
        max_length=40,
        default="heart_artifact_not_found",
        description=f"心脏伪影 {' '.join(['--'.join([str(enum.name), str(HeartArtifactEnum.get_enum_values(enum.value))]) for enum in HeartArtifactEnum])}",
    )
    position = fields.CharField(
        max_length=40,
        default="normal_position",
        description=f"体位 {' '.join(['--'.join([str(enum.name), str(PositionEnum.get_enum_values(enum.value))]) for enum in PositionEnum])}",
    )
    image_quality = fields.CharField(
        max_length=40,
        default="normal_quality",
        description=f"图像质量 {' '.join(['--'.join([str(enum.name), str(ImageQualityEnum.get_enum_values(enum.value))]) for enum in ImageQualityEnum])}",
    )
    image_integrity = fields.CharField(
        max_length=40,
        default="normal_integrity",
        description=f"图像完整性 {' '.join(['--'.join([str(enum.name), str(ImageIntegrityEnum.get_enum_values(enum.value))]) for enum in ImageIntegrityEnum])}",
    )
    specialty = fields.CharField(
        max_length=40,
        default="no_specialty",
        description=f"特殊案例 {' '.join(['--'.join([str(enum.name), str(SpecialtyEnum.get_enum_values(enum.value))]) for enum in SpecialtyEnum])}",
    )


class StudyAudit(BaseUpsertModel):
    study: fields.OneToOneRelation[Study] = fields.OneToOneField(
        "base.Study", related_name="study_audit"
    )
    # 未审核，初审中，初审完成，终审中，终审完成
    check_status = fields.CharField(
        max_length=30,
        description=f"用户审核状态: {' '.join(['--'.join([str(enum.name), str(enum.value)]) for enum in CheckStatusEnum])}",
        null=True,
    )
    first_check_user: fields.ForeignKeyRelation[User] = fields.ForeignKeyField(
        "base.User", related_name="study_audit_first", null=True
    )
    first_status = fields.CharField(
        max_length=64,
        null=True,
        description=f"一审状态： {' '.join(['--'.join([str(enum.name), str(enum.value)]) for enum in FirstUserCheckStatus])}",
    )
    first_mark = fields.TextField(null=True)
    first_check_time = fields.DatetimeField(null=True)
    first_classifier = fields.JSONField(null=True, description="first_classifier")
    first_report = fields.JSONField(null=True, description="first_report")

    last_check_user: fields.ForeignKeyRelation[User] = fields.ForeignKeyField(
        "base.User", related_name="study_audit_last", null=True
    )
    last_status = fields.CharField(
        max_length=64,
        null=True,
        description=f"二审状态：{' '.join(['--'.join([str(enum.name), str(enum.value)]) for enum in LastUserCheckStatus])}",
    )
    last_status_ai = fields.CharField(
        max_length=64,
        null=True,
        description=f"二审ai审状态： {' '.join(['--'.join([str(enum.name), str(enum.value)]) for enum in FirstUserCheckStatus])}",
    )
    last_mark = fields.TextField(null=True)
    last_check_time = fields.DatetimeField(null=True)
    last_classifier = fields.JSONField(null=True, description="last_classifier")
    last_report = fields.JSONField(null=True, description="last_report")


class SeriesAuditLog(BaseUpsertModel):
    """
    序列审核记录
    """

    series: fields.ForeignKeyRelation[Series] = fields.ForeignKeyField(
        "base.Series", related_name="series_audits"
    )
    user: fields.ForeignKeyRelation[User] = fields.ForeignKeyField(
        "base.User", related_name="audit_logs"
    )
    ai_audit = fields.JSONField(null=True, description="ai结果")
    user_audit = fields.JSONField(null=True, description="用户标注结果")


class DictServerData(BaseUpsertModel):
    """字典缓存服务"""

    url_path = fields.CharField(max_length=128, unique=True)
    dict_data = fields.JSONField(null=True)
