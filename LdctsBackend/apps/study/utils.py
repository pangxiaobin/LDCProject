#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : utils.py
import asyncio
import os
import re
import uuid
from base64 import b64encode
from io import BytesIO
from collections import defaultdict

import SimpleITK as sitk
from PIL import Image
import numpy as np

from common.globals_enums import CheckStatusEnum
from common.log import logger
from conf.settings import settings
from aiohttp import ClientSession, ClientError

from core.error_enums.exception import ServerException
from models.base import Study, Series, StudyAudit, DictServerData
import traceback


def compress_image(image_data: np.ndarray, output_path):
    # 转为png时，需要转为无符号数据
    image = Image.fromarray(image_data.astype("uint16"))
    # resized_image = image.resize((512, 512))
    # resized_image.save(output_path)
    image.save(str(output_path))


async def download_nifti_file(nifti_url, timeout=300, retries=3):
    file_name = uuid.uuid4().hex + nifti_url.split("=")[-1]
    file_path = settings.NIFTI_TEMP_DIR / file_name

    for attempt in range(retries):
        try:
            async with ClientSession() as session:
                async with session.get(nifti_url, timeout=timeout) as response:
                    with open(file_path, "wb") as temp_file:
                        while True:
                            chunk = await response.content.read(1024)
                            if not chunk:
                                break
                            temp_file.write(chunk)
                    return file_path
        except ClientError as e:
            logger.error(f"Download attempt {attempt + 1} for {nifti_url} failed: {e}")
            if attempt < retries - 1:
                logger.warning("Retrying...")
            else:
                logger.error(f"Max retries reached. Download failed for {nifti_url}.")
                raise
        except Exception as e:
            logger.error(f"An unexpected error occurred during download: {e}")
            logger.exception(e)
            try:
                # Delete the file in case of an error
                os.remove(file_path)
            except Exception as delete_error:
                logger.error(f"Error deleting file {file_path}: {delete_error}")


async def nifti_to_png(
    nifti_url, study_id, series_filename, recon, nifti_size, breath_artifact
):
    """
    保存nifti
    """
    # 读取NIfTI文件
    series_filename_path = series_filename.replace(".", "_")
    logger.info(f"nifti_url:{nifti_url}")
    try:
        temp_file_path = await download_nifti_file(nifti_url)
        if not temp_file_path:
            logger.error(f"download_nifti_filer error:{nifti_url}")
            return
        # 使用SimpleITK读取临时文件中的NIfTI数据
        itk_img = sitk.ReadImage(temp_file_path)
        #  itk_img.GetSize() ---> xyz
        direction = itk_img.GetDirection()
        origin = itk_img.GetOrigin()
        array = sitk.GetArrayFromImage(itk_img)

        # 确定像素数据是否为无符号类型
        unsigned = True if array.min() >= 0 else False

        if unsigned:
            # 检查最大像素值是否超过了16位无符号整数的最大值
            if array.max() >= pow(2, 16):
                array = array / (array.max() / (pow(2, 16) - 1))
            array = array.astype("uint16")
        else:
            if array.max() >= pow(2, 15):
                array = array / (array.max() / (pow(2, 15) - 1))
            array = array.astype("int16")
        shape = array.shape
        *pixel_spacing, slice_thickness = itk_img.GetSpacing()
        # 深度，高度，宽度 z, y, x
        # 轴向（Axial）、冠状（Coronal）和矢状（Sagittal）
        if settings.DEBUG:
            output_path_dir = settings.NIFTI_PNG_PATH_TEM / series_filename_path
        else:
            output_path_dir = settings.NIFTI_PNG_PATH / series_filename_path
        if not output_path_dir.exists():
            output_path_dir.mkdir(parents=True, exist_ok=True)

        defaults = {
            "recon": recon,
            "instance_num": shape[0],
            "image_orientation_patient": "\\".join([str(x) for x in direction]),
            "image_position_patient": "\\".join([str(x) for x in origin]),
            "pixel_spacing": "\\".join([str(x) for x in pixel_spacing]),
            "nifti_size": nifti_size,
            "breath_artifact": breath_artifact,
        }
        if not await Series.filter(
            study_id=study_id, series_filename=series_filename
        ).exists():
            await Series.create(
                study_id=study_id, series_filename=series_filename, **defaults
            )
        else:
            await Series.filter(
                study_id=study_id, series_filename=series_filename
            ).update(**defaults)
        for i in range(shape[0]):
            pixel_data = array[i, ...]
            # #  归一化
            # slice_normalized = (PixelData - np.min(PixelData)) / (np.max(PixelData) - np.min(PixelData))
            # slice_8bit = (slice_normalized * 255).astype('uint8')
            output_path = output_path_dir / f"{i}.png"
            if output_path.exists():
                continue
            compress_image(pixel_data, output_path)
    except Exception as e:
        logger.error(f"download {nifti_url} error: {traceback.format_exc()}")
    finally:
        try:
            # 删除文件
            os.remove(temp_file_path)
            logger.info("文件已成功删除。")
        except Exception as e:
            logger.error(f"删除文件时出错: {e}")


async def save_study(data: dict):
    """
    保存study
    {
      "count": 4,
      "patient.studyid": "org2.X0117.20231201",
      "patient.age": 27,
      "patient.gender": "gender_female",
      "status.airesult": "airesult_success",
      "timestamp": {
        "patient.study_datetime": "2023/12/01 16:08:30",
        "patient.save_datetime": "2023/12/02 10:00:00",
        "patient.in_queue_datetime": "2023/12/02 14:02:00",
        "patient.prediction_datetime": "2023/12/02 16:02:00"
      },
      "nifti": [
        {
          "nifti.filename": "org2.X0117.20231201.lung_0625.nii.gz",
          "nifti.recon": "nifti_recon_lung",
          "nifti.md5": "fa9dfb7eb0278205cd95c3dddc44ebd5",
          "nifti.filesize": 97782999,
          "nifti.download": "http://123.56.82.224:8002/download?file_name=org2.X0117.20231201.lung_0625.nii.gz"
        },
        {
          "nifti.filename": "org2.X0117.20231201.mediastinum_0625.nii.gz",
          "nifti.recon": "nifti_recon_mediastinal",
          "nifti.md5": "b3c6ecd52e5079624a1291143e77b09e",
          "nifti.filesize": 88556719,
          "nifti.download": "http://123.56.82.224:8002/download?file_name=org2.X0117.20231201.mediastinum_0625.nii.gz"
        },
        {
          "nifti.filename": "org2.X0117.20231201.lung_10.nii.gz",
          "nifti.recon": "nifti_recon_lung",
          "nifti.md5": "686d2fc75ed896009f4d47f90b3b9986",
          "nifti.filesize": 18808235,
          "nifti.download": "http://123.56.82.224:8002/download?file_name=org2.X0117.20231201.lung_10.nii.gz"
        },
        {
          "nifti.filename": "org2.X0117.20231201.mediastinum_10.nii.gz",
          "nifti.recon": "nifti_recon_mediastinal",
          "nifti.md5": "ec9815d7654bb800f360f3a63ccbeb6f",
          "nifti.filesize": 16221233,
          "nifti.download": "http://123.56.82.224:8002/download?file_name=org2.X0117.20231201.mediastinum_10.nii.gz"
        }
      ],
      "ai_result": {
        "ai_task_id": "org2.X0117.20231201_20231202100000",
        "label": [
          {
            "nifti-label.filename": "org2.X0117.20231201.lung_0625.label1.nii.gz",
            "nifti-label.file_type": "label_file_type_orgnism_seg",
            "nifti.filename": "org2.X0117.20231201.lung_0625.nii.gz",
            "nifti-label.download": "http://123.56.82.224:8002/download?file_name=org2.X0117.20231201.lung_0625.label1.nii.gz"
          },
          {
            "nifti-label.filename": "org2.X0117.20231201.lung_0625.label2.nii.gz",
            "nifti-label.file_type": "label_file_type_lesion_seg",
            "nifti.filename": "org2.X0117.20231201.lung_0625.nii.gz",
            "nifti-label.download": "http://123.56.82.224:8002/download?file_name=org2.X0117.20231201.lung_0625.label2.nii.gz"
          }
        ],
        "lesion": [
          {
            "desc.label_value": 2,
            "desc.central_slice": 100,
            "nifti-label.filename": "org2.X0117.20231201.lung_0625.label2.nii.gz",
            "desc.size": 20,
            "desc.volume": 30
          }
        ],
        "classifier": {
          "classifer.stent": "classifier_stent_invisible",
          "classifier.pacemaker": "classifier_pacemaker_lesion_invisible",
          "classifier.chestwall": "classifier_chestvall_lesion_invisible",
          "classifier.vertebrae": "classifier_vertebrae_lesion_invisible",
          "classifier.mediastinum": "classifier_mediastinum_lesion_invisible"
        },
        "report": {
          "report.finding": "",
          "report.diagnosis": ""
        }
      }
    }
    """
    try:
        study_instance_id = data.get("patient.studyid")
        patient_age = data.get("patient.age")
        patient_gender = data.get("patient.gender")
        save_time = data.get("timestamp").get("patient.save_datetime")
        study_time = data.get("timestamp").get("patient.study_datetime")
        ai_status = data.get("status.airesult")
    except Exception as e:
        logger.error(f"存储失败{data}")
        return
    if ai_status == "airesult_success":
        ai_result = data.get("ai_result")
    else:
        ai_result = None
    defaults = {
        "patient_age": patient_age,
        "patient_gender": patient_gender,
        "save_time": save_time,
        "study_time": study_time,
        "ai_status": ai_status,
        "study_ai_result": ai_result,
    }
    if await Study.filter(study_instance_id=study_instance_id).exists():
        await Study.filter(study_instance_id=study_instance_id).update(**defaults)
        study = await Study.filter(study_instance_id=study_instance_id).first()
        nifti_list = data.get("nifti", [])
        for item in nifti_list:
            nifti_url = item.get("nifti.download")
            study_id = study.id
            series_filename = item.get("nifti.filename")
            recon = item.get("nifti.recon")
            breath_artifact = item.get("nifti.breath_artifact", "")
            nifti_size = item.get("nifti.size", [512, 512, 0])
            if not await Series.filter(
                study_id=study_id, series_filename=series_filename
            ).exists():
                await nifti_to_png(
                    nifti_url,
                    study_id,
                    series_filename,
                    recon,
                    nifti_size,
                    breath_artifact,
                )
            else:
                await Series.filter(
                    study_id=study_id, series_filename=series_filename
                ).update(recon=recon, breath_artifact=breath_artifact)
        logger.info(f"更新{study_instance_id}成功")
        return
    else:
        study = await Study.create(study_instance_id=study_instance_id, **defaults)
    # 创建审核信息
    if not await StudyAudit.filter(study_id=study.id).exists():
        await StudyAudit.create(
            study_id=study.id, check_status=CheckStatusEnum.audit_not_audit
        )
        logger.info(f"新建{study_instance_id}成功")
    nifti_list = data.get("nifti", [])
    for item in nifti_list:
        nifti_url = item.get("nifti.download")
        study_id = study.id
        series_filename = item.get("nifti.filename")
        recon = item.get("nifti.recon")
        nifti_size = item.get("nifti.size", [512, 512, 0])
        breath_artifact = item.get("nifti.breath_artifact", "")
        await nifti_to_png(
            nifti_url, study_id, series_filename, recon, nifti_size, breath_artifact
        )


async def semaphore_worker(item, semaphore):
    """
    控制并发量
    """
    async with semaphore:
        await save_study(item)


async def background_save_study(data_list: list):
    """
    异步存储拉取的数据
    """
    if settings.DEBUG:
        for item in data_list:
            await save_study(item)
    else:
        # 设置最大并发数
        semaphore = asyncio.Semaphore(5)

        tasks = [semaphore_worker(item, semaphore) for item in data_list]
        await asyncio.gather(*tasks)
    logger.info("background save study done")


def conversion_label_data_dict(data: dict) -> dict:
    label_dict = {}
    for _, val in data.items():
        level1_children = val.get("children")
        parent_parent_key = val.get("key")
        for _, val2 in level1_children.items():
            parent_name = val2.get("chinese_name")
            parent_key = val2.get("key")
            level2_children = val2.get("children")
            if level2_children:
                for _, val3 in level2_children.items():
                    chinese_name = val3.get("chinese_name")
                    label = val3.get("label")
                    label_key = val3.get("key")
                    label_dict[label] = {
                        "parent_name": parent_name,
                        "parent_key": parent_key,
                        "parent_parent_key": parent_parent_key,
                        "label_chinese_name": chinese_name,
                        "label_key": label_key,
                    }
            else:
                chinese_name = val2.get("chinese_name")
                label = val2.get("label")
                label_key = val2.get("key")
                label_dict[label] = {
                    "parent_name": parent_name,
                    "parent_key": parent_key,
                    "parent_parent_key": parent_parent_key,
                    "label_chinese_name": chinese_name,
                    "label_key": label_key,
                }
    return label_dict


def conversion_anatomy_data_dict(data: dict) -> dict:
    anatomy_data = {}
    for key1, val in data.items():
        level1_children = val.get("children")
        if level1_children:
            for key2, val2 in level1_children.items():
                level2_children = val2.get("children")
                if level2_children:
                    for key3, val3 in level2_children.items():
                        anatomy_data[key3] = val3.get("chinese_name", "")
                else:
                    anatomy_data[key2] = val.get("chinese_name", "")
        else:
            anatomy_data[key1] = val.get("chinese_name", "")
    return anatomy_data


async def get_dict_data(url_path: str):
    """
    下载数据
    :param url_path:
    :return:
    """
    dict_server = settings.DICT_DARA_SERVER
    if url_path == "lesion_detail":
        url = f"{dict_server}lesion"
    elif url_path == "anatomy_detail":
        url = f"{dict_server}anatomy"
    else:
        url = f"{dict_server}{url_path}"
    async with ClientSession() as session:
        async with session.get(url) as response:
            try:
                response_data = await response.json()
                if response_data.get("status") == "success":
                    if url_path == "lesion":
                        detail_data = conversion_label_data_dict(
                            response_data.get("detail")
                        )
                    elif url_path == "anatomy":
                        detail_data = conversion_anatomy_data_dict(
                            response_data.get("detail")
                        )
                    else:
                        detail_data = response_data.get("detail")
                    if await DictServerData.filter(url_path=url_path).exists():
                        await DictServerData.filter(url_path=url_path).update(
                            dict_data=detail_data
                        )
                    else:
                        await DictServerData.create(
                            url_path=url_path, dict_data=detail_data
                        )

            except Exception as e:
                logger.error(f"获取{url} 失败，{e}")


async def update_dict_data():
    """
    更新字典服务的数据
    :return:
    """
    update_all_key = [
        {"key": "anatomy", "value": "解剖相关字典定义"},
        {"key": "anatomy_detail", "value": "解剖相关字典定义详细版本"},
        {"key": "lesion", "value": "病灶相关字典定义"},
        {"key": "lesion_detail", "value": "病灶相关字典定义详细版"},
        {"key": "desc", "value": "病灶级别精细描述定义"},
        {"key": "report", "value": "报告相关字典定义"},
        {"key": "classifier", "value": "AI结果分类输出"},
        {"key": "patient", "value": "患者相关字典定义"},
        {"key": "status", "value": "客户数据状态定义"},
        {"key": "nifti", "value": "3D影像相关的信息定义"},
        {"key": "label", "value": "label相关的信息定义"},
    ]
    if settings.DEBUG:
        for item in update_all_key:
            await get_dict_data(item.get("key"))
    else:
        tasks = [get_dict_data(item.get("key")) for item in update_all_key]
        await asyncio.gather(*tasks)


async def update_classifier(classifier: dict) -> list[dict]:
    """
    "classifier": {
          "classifer.stent": "0",
          "classifier.pacemaker": "1",
          "classifier.chestwall": "0",
          "classifier.vertebrae": "1",
          "classifier.mediastinum": "0"
    }
    :param classifier:
    :return:
    """
    dict_classifier_obj = await DictServerData.get(url_path="classifier")
    dict_data = dict_classifier_obj.dict_data
    data_list = []
    for key, val in classifier.items():
        tem_dict = {"classifier_name": key, "is_visible": val}
        chinese_name = dict_data.get(key).get("chinese_name")
        tem_dict["chinese_name"] = chinese_name
        data_list.append(tem_dict)
    return data_list


def match_series_label_name(series_name: str, label_name: str) -> bool:
    """
     匹配series_name和label_name
    :param series_name:
    :param label_name:
    :return:
    """
    pattern = r"^(.+?\..+?\..+?\..+?)\."
    series_name_match = re.match(pattern, series_name)
    label_name_match = re.match(pattern, label_name)
    if series_name_match.group(1) == label_name_match.group(1):
        return True
    else:
        return False


def npy2annostr(arr):
    img = Image.fromarray(arr.astype("uint8"))
    b = BytesIO()
    img.save(b, "PNG")
    return b64encode(b.getvalue()).decode()


async def download_label_marks(url: str):
    """
    下载mask
    :param url:
    """
    try:
        temp_file_path = await download_nifti_file(url)
        # 使用SimpleITK读取临时文件中的NIfTI数据
        itk_img = sitk.ReadImage(temp_file_path, sitk.sitkInt32)
        array = sitk.GetArrayFromImage(itk_img)
        ai_label_mask_list = []
        for slice_index in range(array.shape[0]):
            tem = {}
            if array[slice_index].max() > 0:
                slice_array = array[slice_index, :, :]
                tem[slice_index] = npy2annostr(slice_array)
                ai_label_mask_list.append(tem)
        return ai_label_mask_list
    except Exception as e:
        logger.error(f"download {url} error: {e}")
    finally:
        try:
            # 删除文件
            os.remove(temp_file_path)
            print("文件已成功删除。")
        except Exception as e:
            print(f"删除文件时出错: {e}")


async def get_label_mask(nifti_filename: str, desc_contained_voxel, label_val):
    """
    生成mask
    :param nifti_filename:
    :param desc_contained_voxel:
    :param label_val:
    :return:
    """
    series = await Series.filter(series_filename=nifti_filename).first()
    x, y, _ = series.nifti_size
    ai_label_mask_list = []
    ai_label_mask_center = []
    for key, val in desc_contained_voxel.items():
        mask_array = np.zeros((x, y), dtype=np.uint8)
        for xy in val:
            mask_array[xy[1], xy[0]] = label_val  # 注意，numpy数组的索引方式为[y, x]
        tem = {key: npy2annostr(mask_array)}
        ai_label_mask_list.append(tem)
        point = get_center_point(val)
        ai_label_mask_center.append({key: point})
    return ai_label_mask_list, ai_label_mask_center


def get_center_point(mask_values):
    x_values = [point[0] for point in mask_values]
    y_values = [point[1] for point in mask_values]

    min_x = min(x_values)
    max_x = max(x_values)
    min_y = min(y_values)
    max_y = max(y_values)
    center_point = [(max_x + min_x) // 2, (max_y + min_y) // 2]
    radius = max(max_x - min_x, max_y - min_y) // 2
    return [center_point, radius]


async def get_label_name_and_parent_name(label_vale) -> dict:
    dict_classifier_obj = await DictServerData.get(url_path="lesion")
    dict_data = dict_classifier_obj.dict_data
    result = dict_data.get(str(label_vale), {})
    if result:
        return result
    else:
        raise ServerException(
            10009,
            cn_msg=f"label {label_vale} 的信息不存在",
            en_msg=f"label {label_vale} info not exist",
        )


def group_lesion(lesion: list[dict]):
    try:
        grouped_dict = defaultdict(list)

        # 根据parent_name进行分组
        for item in lesion:
            parent_name = item["parent_name"]
            grouped_dict[parent_name].append(item)
        result_list = []
        for key, value in grouped_dict.items():
            if value:
                parent_key = value[0].get("parent_key")
                parent_parent_key = value[0].get("parent_key")
            else:
                parent_key = ""
                parent_parent_key = ""
            tem = {
                "parent_name": key,
                "children": value,
                "parent_key": parent_key,
                "parent_parent_key": parent_parent_key,
            }
            result_list.append(tem)
        return result_list
    except Exception as e:
        logger.error(f"分组错误:{e}")
        return lesion


async def get_desc_location_name(location):
    dict_classifier_obj = await DictServerData.get(url_path="anatomy")
    dict_data = dict_classifier_obj.dict_data
    result = dict_data.get(location, "")
    if result:
        return result
    else:
        raise ServerException(
            10009,
            cn_msg=f"location {location} 的信息不存在",
            en_msg=f"location {location} info not exist",
        )


if __name__ == "__main__":
    pass
