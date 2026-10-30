#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : error.py

from .exception import ServerException

ParamError = ServerException(10000, "参数错误", "param error")

UserNotExist = ServerException(10001, "用户不存在", "user not exist")
UserPasswordError = ServerException(10002, "用户名或密码错误", "username or password error")
UserHasExist = ServerException(10003, "用户已存在", "user has already exist")
OldPasswordError = ServerException(10004, "旧密码错误", "old password error")
PasswordError = ServerException(10005, "密码错误", "password error")


RequestThirdPartyError = ServerException(
    10006, "请求第三方错误", "request for third-party error"
)

StudyAuditCreateError = ServerException(
    10007, cn_msg="创建错误，需检查状态", en_msg="create Error"
)
StudyAuditUpdateError = ServerException(10008, cn_msg="修改错误", en_msg="update Error")

StudyAuditNotExist = ServerException(
    10009, cn_msg="StudyAudit 不存在", en_msg="StudyAudit not exist"
)

DictInfoNotExist = ServerException(
    10010, cn_msg="字典服务中值不存在", en_msg="dict data info not exist"
)

StudyNotExist = ServerException(10011, cn_msg="Study 不存在", en_msg="Study not exist")

DataDictNotExist = ServerException(
    10012, cn_msg="DataDict 不存在", en_msg="DataDict not exist"
)

ExportError = ServerException(
    10013, cn_msg="不支持未审核导出", en_msg="Unapproved exports are not supported"
)

SeriesQualityControlCreateUpdateError = ServerException(
    10014, cn_msg="创建或者更新失败", en_msg="create or update error"
)

SeriesDotExist = ServerException(10015, cn_msg="series 不存在", en_msg="series not exist")
