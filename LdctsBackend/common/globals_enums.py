#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : globals_enums.py
from enum import Enum


class RoleEnum(str, Enum):
    """
    角色
    """

    ADMIN = "1"
    NORMAL = "2"
    FIRST_AUDIT = "3"
    LAST_AUDIT = "4"


class CheckStatusEnum(str, Enum):
    """
    审核状态
    未审核，初审中，初审完成，终审中，终审完成
    """

    audit_not_audit = "audit_not_audit"
    audit_in_first_round = "audit_in_first_round"
    audit_finish_first_round = "audit_finish_first_round"
    audit_in_final_round = "audit_in_final_round"
    audit_finish_final_round = "audit_finish_final_round"

    @classmethod
    def index(cls, status):
        return {
            "audit_not_audit": 0,
            "audit_in_first_round": 1,
            "audit_finish_first_round": 2,
            "audit_in_final_round": 3,
            "audit_finish_final_round": 4,
        }.get(status)


class FirstUserCheckStatus(str, Enum):
    """
    用户审核状态
    """

    ai_correct = "aicomment_ai_correct"
    ai_not_correct = "aicomment_ai_not_correct"


class LastUserCheckStatus(str, Enum):
    auditor_correct = "auditorcomment_first_auditor_correct"
    auditor_not_correct = "auditorcomment_first_auditor_not_correct"


class BreathArtifactEnum(str, Enum):
    breath_artifact_not_found = "breath_artifact_not_found"
    breath_artifact_low = "breath_artifact_low"
    breath_artifact_medium = "breath_artifact_medium"
    breath_artifact_high = "breath_artifact_high"

    @staticmethod
    def get_enum_values(val):
        return {
            "breath_artifact_not_found": "无伪影",
            "breath_artifact_low": "有伪影,不影响诊断",
            "breath_artifact_medium": "有伪影,勉强可以诊断",
            "breath_artifact_high": "伪影严重,不能诊断",
        }.get(val)


class MetalArtifactEnum(str, Enum):
    metal_artifact_not_found = "metal_artifact_not_found"
    metal_artifact_low = "metal_artifact_low"
    metal_artifact_medium = "metal_artifact_medium"
    metal_artifact_high = "metal_artifact_high"

    @staticmethod
    def get_enum_values(val):
        return {
            "metal_artifact_not_found": "无伪影",
            "metal_artifact_low": "有伪影,不影响诊断",
            "metal_artifact_medium": "有伪影,勉强可以诊断",
            "metal_artifact_high": "伪影严重,不能诊断",
        }.get(val)


class HeartArtifactEnum(str, Enum):
    heart_artifact_not_found = "heart_artifact_not_found"
    heart_artifact_low = "heart_artifact_low"
    heart_artifact_medium = "heart_artifact_medium"
    heart_artifact_high = "heart_artifact_high"

    @staticmethod
    def get_enum_values(val):
        return {
            "heart_artifact_not_found": "无伪影",
            "heart_artifact_low": "有伪影,不影响诊断",
            "heart_artifact_medium": "有伪影,勉强可以诊断",
            "heart_artifact_high": "伪影严重,不能诊断",
        }.get(val)


class PositionEnum(str, Enum):
    normal_position = "normal_position"
    prone_position = "prone_position"
    oblique_position = "oblique_position"

    @staticmethod
    def get_enum_values(val):
        return {
            "normal_position": "正常体位",
            "prone_position": "俯卧位",
            "oblique_position": "倾斜位",
        }.get(val)


class ImageQualityEnum(str, Enum):
    normal_quality = "normal_quality"
    low_quality = "low_quality"
    bad_quality = "bad_quality"

    @staticmethod
    def get_enum_values(val):
        return {
            "normal_quality": "正常质量",
            "low_quality": "质量偏低,勉强可以诊断",
            "bad_quality": "图像质量低,不能诊断",
        }.get(val)


class ImageIntegrityEnum(str, Enum):
    normal_integrity = "normal_integrity"
    low_integrity = "low_integrity"
    bad_integrity = "bad_integrity"

    @staticmethod
    def get_enum_values(val):
        return {
            "normal_integrity": "完整图像",
            "low_integrity": "部分缺失,仍可用",
            "bad_integrity": "图像缺失,不能诊断",
        }.get(val)


class SpecialtyEnum(str, Enum):
    no_specialty = "no_specialty"
    specialty_case = "specialty_case"

    @staticmethod
    def get_enum_values(val):
        return {
            "no_specialty": "正常案例",
            "specialty_case": "特殊案例",
        }.get(val)
