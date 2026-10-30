#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : base_response.py
from typing import Union

from fastapi.encoders import jsonable_encoder
from starlette import status
from starlette.responses import JSONResponse


def resp_200(
    *, data: Union[list, dict, str] = None, msg: str = "Success", **kwargs
) -> JSONResponse:
    content = {"code": 200, "msg": msg, "data": data}
    if kwargs:
        content.update(**kwargs)
    return JSONResponse(
        status_code=status.HTTP_200_OK, content=jsonable_encoder(content)
    )
