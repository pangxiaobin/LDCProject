#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : utils.py
import re
import time
from pathlib import Path
from typing import AnyStr, Sequence

from fastapi import File, Request


def get_client_ip(request: Request) -> AnyStr:
    """
    获取客户端ip
    :param request:
    :return:
    """

    client_host = request.headers.get("X-Real-IP")
    if not client_host:
        client_host = request.headers.get("X-Forwarded-For")
    if not client_host:
        client_host = request.client.host
    return client_host


async def save_img(file: File, save_dir: Path) -> str:
    if file:
        image_name = f"{str(int(time.time()))}-{file.filename}"
        save_path = save_dir / image_name
        if not save_path.exists():
            with open(save_path, "wb") as f:
                content = await file.read()
                f.write(content)
        pre_path = str(save_dir).split("media")[-1].replace("/", "")
        image_url = str(Path("media") / pre_path / image_name)
    else:
        image_url = ""
    return image_url


def check_re_match_url(request_url: str, re_exclude_api_url: Sequence[str]) -> bool:
    for i in re_exclude_api_url:
        if re.match(i, request_url):
            return True
    return False
