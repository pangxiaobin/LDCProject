#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : curd.py
import os
import shutil

from typing import Union

from tortoise.exceptions import DoesNotExist
from tortoise.expressions import Q
from tortoise.queryset import QuerySet

from conf.settings import settings
from core.base_schemas import TokenData
from core.error_enums.error import (
    StudyAuditCreateError,
    StudyAuditUpdateError,
    StudyNotExist,
    UserNotExist,
    StudyAuditNotExist,
    ExportError,
    SeriesQualityControlCreateUpdateError,
    SeriesDotExist,
    ParamError,
)
from models.v_models import V_Study
from models.base import (
    Series,
    Study,
    StudyAudit,
    SeriesAuditLog,
    User,
    SeriesQualityControl,
    DictServerData,
)
from common.globals_enums import RoleEnum, CheckStatusEnum
from .func_picker import Picker
from .schema import (
    SeriesDetail,
    StudyAuditCreate,
    StudyAuditClassifierUpdate,
    StudyAuditUpdate,
    SeriesAuditLogCreate,
    StudyDelete,
    SeriesQualityControlCreate,
    SeriesQualityControlDetail,
)
from .utils import (
    update_classifier,
    match_series_label_name,
    download_label_marks,
    get_label_name_and_parent_name,
    group_lesion,
    get_desc_location_name,
    get_label_mask,
)


class StudyModel:
    @staticmethod
    async def get_study_list(
        page: int,
        page_size: int = 20,
        ai_status: str = "",
        check_status: str = "",
        study_instance_id: str = "",
        user_id: Union[int, None, str] = None,
    ) -> (QuerySet, int):
        """
        获取用户列表
        """
        offset = (page - 1) * page_size
        query_set = V_Study.all()
        if ai_status:
            query_set = query_set.filter(ai_status=ai_status)
        if check_status:
            query_set = query_set.filter(check_status=check_status)
        if study_instance_id:
            query_set = query_set.filter(study_instance_id__icontains=study_instance_id)
        if user_id:
            try:
                user = await User.get(id=user_id)
            except DoesNotExist:
                raise UserNotExist
            role = user.role
            if role == RoleEnum.FIRST_AUDIT:
                query_set = query_set.filter(first_check_user_id=user_id)
            elif role == RoleEnum.LAST_AUDIT:
                query_set = query_set.filter(last_check_user_id=user_id)
        total = await query_set.count()
        data_list = await query_set.offset(offset).limit(page_size).order_by("-id")
        return data_list, total

    @staticmethod
    async def study_delete(study_in: StudyDelete):
        # 删除study 数据
        study_ids = study_in.study_ids
        for study_id in study_ids:
            try:
                study = await Study.get(id=study_id)
            except DoesNotExist:
                continue
            series = await study.series
            # 删除序列下的png
            for ser in series:
                series_filename_path = f"{ser.series_filename.replace('.', '_')}"
                if settings.DEBUG:
                    output_path_dir = settings.NIFTI_PNG_PATH_TEM / series_filename_path
                else:
                    output_path_dir = settings.NIFTI_PNG_PATH / series_filename_path
                shutil.rmtree(str(output_path_dir), ignore_errors=True)
        await Study.filter(id__in=study_ids).delete()


class SeriesModel:
    @staticmethod
    async def get_series_by_study_id(study_id: int, role: str) -> dict:
        """
        获取影像列表
        如果是普通角色：只获取影像数据
        如果是初审医生: 获取
        """
        try:
            study_info = await Study.get(id=study_id).values(
                "study_instance_id",
                "patient_age",
                "patient_gender",
                "study_ai_result",
                "ai_status",
            )
        except DoesNotExist:
            raise StudyNotExist
        series = await Series.filter(study_id=study_id)

        study_ai_result = study_info.pop("study_ai_result", {})
        ai_classifier = study_ai_result.get("classifier") if study_ai_result else None
        if ai_classifier:
            ai_classifier = await update_classifier(ai_classifier)
        ai_report = study_ai_result.get("report") if study_ai_result else None
        study_audit = await StudyAudit.filter(study_id=study_id).first()
        series_data = [
            SeriesDetail.model_dump(SeriesDetail.model_validate(s, strict=False))
            for s in series
        ]
        try:
            dict_obj = await DictServerData.get(url_path="nifti")
            dict_data = dict_obj.dict_data
        except DoesNotExist:
            dict_data = {}
        for series in series_data:
            recon = series.get("recon", "")
            if recon:
                try:
                    series["recon"] = (
                        dict_data.get("nifti.recon")
                        .get("values")
                        .get(recon)
                        .get("chinese_name")
                    )
                except Exception:
                    pass
            breath_artifact = series.get("breath_artifact", "")
            if breath_artifact:
                try:
                    series["breath_artifact"] = (
                        dict_data.get("nifti.breath_artifact")
                        .get("values")
                        .get(breath_artifact)
                        .get("chinese_name")
                    )
                except Exception:
                    pass
        study_info["study_id"] = study_id
        study_info["ai_report"] = ai_report
        study_info["series"] = series_data
        study_info["ai_classifier"] = ai_classifier
        study_info["first_classifier"] = study_audit.first_classifier
        study_info["last_classifier"] = study_audit.last_classifier
        study_info["first_report"] = study_audit.first_report
        study_info["last_report"] = study_audit.last_report
        study_info["first_status"] = study_audit.first_status
        study_info["first_mark"] = study_audit.first_mark
        study_info["last_status"] = study_audit.last_status
        study_info["last_status_ai"] = study_audit.last_status_ai
        study_info["last_mark"] = study_audit.last_mark
        return study_info

    @staticmethod
    async def get_series_anno_by_series_id(series_id: int) -> dict:
        try:
            series_obj = await Series.get(id=series_id)
        except DoesNotExist:
            raise SeriesDotExist
        series_filename = series_obj.series_filename
        result = {"id": series_id, "series_filename": series_filename}
        try:
            series_quality_control = await SeriesQualityControl.get(series_id=series_id)
            quality_control_dict = await SeriesQualityControlDetail.from_tortoise_orm(
                series_quality_control
            )
            quality_control = quality_control_dict.model_dump()
        except DoesNotExist:
            quality_control = None
        result["quality_control"] = quality_control
        study = await series_obj.study.first()
        study_ai_result = study.study_ai_result
        # 把预测的label 放入到对应的序列中
        ai_lesion = study_ai_result.get("lesion") if study_ai_result else []
        labels = study_ai_result.get("label") if study_ai_result else []
        ai_lesion_series = []
        for ai_lesion_item in ai_lesion:
            label_filename = ai_lesion_item.get("nifti-label.filename")
            if match_series_label_name(series_filename, label_filename):
                for label_item in labels:
                    if label_filename == label_item.get("nifti-label.filename"):
                        download_url = label_item.get("nifti-label.download")
                        label_val = ai_lesion_item.get("desc.label_value")
                        label_name_parent_name = await get_label_name_and_parent_name(
                            label_val
                        )
                        nifti_filename = label_item.get("nifti.filename")  # 用来查询Series
                        desc_contained_voxel = ai_lesion_item.pop(
                            "desc.contained_voxel", []
                        )
                        label_marks, label_marks_point = await get_label_mask(
                            nifti_filename, desc_contained_voxel, label_val
                        )
                        ai_lesion_item["label_marks"] = label_marks
                        ai_lesion_item["label_marks_point"] = label_marks_point
                        ai_lesion_item.update(**label_name_parent_name)
                        location_name = ai_lesion_item.get("desc.location")
                        ai_lesion_item[
                            "location_chinese_name"
                        ] = await get_desc_location_name(location_name)
                        ai_lesion_item["is_visible"] = 1

                ai_lesion_series.append(ai_lesion_item)
        ai_lesion_series_group = group_lesion(ai_lesion_series)
        result["ai_lesion_series"] = ai_lesion_series_group
        first_ai_audit = None
        first_user_audit = None
        last_ai_audit = None
        last_user_audit = None
        series_audit_obj = await SeriesAuditLog.filter(series_id=series_id)
        for series_audit_item in series_audit_obj:
            user = await series_audit_item.user.first()
            if user.role == RoleEnum.FIRST_AUDIT:
                first_ai_audit = series_audit_item.ai_audit
                first_user_audit = series_audit_item.user_audit
            elif user.role == RoleEnum.LAST_AUDIT:
                last_ai_audit = series_audit_item.ai_audit
                last_user_audit = series_audit_item.user_audit
        result["first_ai_audit"] = first_ai_audit
        result["first_user_audit"] = first_user_audit
        result["last_ai_audit"] = last_ai_audit
        result["last_user_audit"] = last_user_audit
        return result


class StudyAuditModel:
    @staticmethod
    async def create_study_audit(audit: StudyAuditCreate, token: TokenData):
        study_id = audit.study_id
        study = await Study.get(id=study_id)
        front_status = audit.check_status
        if study.ai_status not in ["airesult_success", "airesult_human_interfere"]:
            raise StudyAuditCreateError
        if await StudyAudit.filter(study_id=study_id).exists():
            backend_status_obj = await StudyAudit.filter(study_id=study_id).first()
            backend_status = backend_status_obj.check_status
        else:
            backend_status = CheckStatusEnum.audit_not_audit
        func = Picker.get_func(backend_status, front_status)
        await func(token, study_id, front_status)

    @staticmethod
    async def upsert_study_audit(audit: StudyAuditUpdate, token: TokenData):
        study_id = audit.study_id
        front_status = audit.check_status
        if not await StudyAudit.filter(study_id=study_id).exists():
            raise StudyAuditUpdateError
        study_audit = await StudyAudit.filter(study_id=study_id).first()
        backend_status = study_audit.check_status
        func = Picker.get_func(backend_status, front_status)
        await func(
            token,
            study_id,
            front_status,
            mark=audit.mark,
            status=audit.status,
            report=audit.report,
        )

    @staticmethod
    async def audit_update_classifier(
        audit: StudyAuditClassifierUpdate, token: TokenData
    ):
        study_id = audit.study_id
        if not await StudyAudit.filter(study_id=study_id).exists():
            raise StudyAuditUpdateError
        study_audit = await StudyAudit.filter(study_id=study_id).first()
        role = token.role
        if role == RoleEnum.FIRST_AUDIT:
            study_audit.first_classifier = audit.classifier
            await study_audit.save()
        elif role == RoleEnum.LAST_AUDIT:
            study_audit.last_classifier = audit.classifier
            await study_audit.save()
        else:
            raise StudyAuditUpdateError

    @staticmethod
    async def study_audit_export(study_id=None, patient_studyid=None) -> dict:
        """
        数据导出
        {
         "patient.studyid": "XW.P100539.01_CT",
         "ai_task_id": "XW.P100539.01_CT_20240229160000",
         "audit.status": xxx,
         "auditors":{
          "level1 auditor": who,
          "level2 auditor": who,
         },
         "report": {
                "report.finding": "xxxxx",
                "report.diagnosis": "xxxxxx"
            },
         "lesions":[
         {   # 要指明是哪个nii，因为一个study中会有多个nii
          "nifti.filename"：“XW.P100440.01_CT.lung_fc_10.label.nii.gz”，
          "removed":[  # 删掉的那些病灶，
           {
            "desc.lesion_uid": "XW.P100440.01_CT.lung_fc_10.label.nii.gz_1"
           }，
           {
            "desc.lesion_uid": "XW.P100440.01_CT.lung_fc_10.label.nii.gz_2"
           }
          ],
          "created":[ # 人工增加的病灶
           {
            "desc.lesion_key": "ground_glass_opacity_malignant",
            "desc.location":"lung_lobe_right_middle",
            "position":[
             {z1 : (x1, y1, x2, y2)},
             {z1 : (x1, y1, x2, y2)},
             {z2 : (x1, y1, x2, y2)},
            ]
           },
          ],
          "classifier":{
           "added":["classifier.chestwall"], # 打上勾的classifier
           "removed":["classifier.mediastinum"],  #去掉勾的classifier
          }
         }
         ]
        }

        }
        """
        if not study_id and not patient_studyid:
            raise ParamError
        if patient_studyid:
            try:
                study = await Study.get(study_instance_id=patient_studyid)
            except DoesNotExist:
                raise StudyNotExist
            study_id = study.id
        if not await StudyAudit.filter(study_id=study_id).exists():
            raise StudyAuditNotExist
        study_audit = await StudyAudit.filter(study_id=study_id).first()
        # 为编辑的不能导出
        if study_audit.check_status == CheckStatusEnum.audit_not_audit:
            raise ExportError
        study = await Study.get(id=study_id)
        study_ai_result = study.study_ai_result
        try:
            first_check_user = await study_audit.first_check_user
            level1_auditor = first_check_user.username
        except Exception:
            level1_auditor = ""
        try:
            last_check_user = await study_audit.last_check_user
            level2_auditor = last_check_user.username
            check_level = "level2"
        except Exception:
            level2_auditor = ""
            check_level = "level1"

        added_classifier = []
        removed_classifier = []
        # 如果有二审，获取二审，否则获取一审的
        if study_audit.last_classifier:
            classifier = study_audit.last_classifier
        else:
            classifier = study_audit.first_classifier
        for item in classifier:
            value = item.get("classifier_name")
            if item["is_visible"]:
                added_classifier.append(value)
            else:
                removed_classifier.append(value)

        result = {
            "patient.studyid": study.study_instance_id,
            "ai_task_id": study_ai_result.get("ai_task_id"),
            "audit.status": study_audit.check_status,
            "auditors": {
                "level1 auditor": level1_auditor,
                "level2 auditor": level2_auditor,
            },
            "report": study_audit.last_report or study_audit.first_report,
        }
        lesions = []
        series = await study.series.all()
        for ser in series:
            tem = {
                "nifti.filename": ser.series_filename,
                "classifier": {
                    "added": added_classifier,  # 打上勾的classifier
                    "removed": removed_classifier,  # 去掉勾的classifier
                },
            }
            try:
                series_quality_control = await SeriesQualityControl.get(
                    series_id=ser.id
                )
                quality_control_dict = (
                    await SeriesQualityControlDetail.from_tortoise_orm(
                        series_quality_control
                    )
                )
                quality_control = quality_control_dict.model_dump()
            except DoesNotExist:
                quality_control = None
            tem["quality_control"] = quality_control

            removed = []

            try:
                series_audit_obj = await SeriesAuditLog.get(
                    series_id=ser.id, user_id=last_check_user.id
                )
            except Exception:
                series_audit_obj = await SeriesAuditLog.get(
                    series_id=ser.id, user_id=first_check_user.id
                )
            ai_audit = series_audit_obj.ai_audit
            if not ai_audit:
                removed = ["ai 未标注"]
            else:
                for ai in ai_audit:
                    children = ai.get("children")
                    for child in children:
                        if not child.get("is_visible"):
                            removed.append({"desc.lesion_uid": child.get("label_key")})
            tem["removed"] = removed
            last_user_audit = series_audit_obj.user_audit
            created = []
            for ua in last_user_audit:
                children = ua["children"]
                for child in children:
                    if child.get("is_visible"):
                        label_marks = child.get("label_marks")
                        position = []
                        for item in label_marks:
                            for key, value in item.items():
                                new_value = []
                                for point in value:
                                    new_value.extend([point["x"], point["y"]])
                                position.append({key: tuple(new_value)})

                        created.append(
                            {
                                "desc.location": child.get("desc.location"),
                                "desc.lesion_key": child.get("desc.lesion_key"),
                                "position": position,
                            }
                        )
            tem["created"] = created
            lesions.append(tem)
        result["lesions"] = lesions
        result["check_level"] = check_level
        return result


class SeriesAuditLogModel:
    @staticmethod
    async def series_audit_create(series_audit: SeriesAuditLogCreate, token: TokenData):
        uid = token.uid
        series_id = series_audit.series_id
        await SeriesAuditLog.update_or_create(
            series_id=series_id,
            user_id=uid,
            defaults={
                "ai_audit": series_audit.ai_audit,
                "user_audit": series_audit.user_audit,
            },
        )


class SeriesQualityControlModel:
    @staticmethod
    async def series_quality_control_create_or_update(
        series_id: int, series_quality_control: SeriesQualityControlCreate
    ):
        try:
            await SeriesQualityControl.update_or_create(
                series_id=series_id,
                defaults=series_quality_control.dict(),
            )
        except Exception as e:
            raise SeriesQualityControlCreateUpdateError
