#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : main.py
"""
fastapi doc:https://fastapi.tiangolo.com/zh/
"""
import uvicorn

from core.server import create_app
from conf.settings import settings

app = create_app()

if __name__ == "__main__":
    if settings.DEBUG:
        uvicorn.run(app="main:app", port=8010, reload=True, log_level="debug")
    else:
        uvicorn.run(app="main:app", port=8010, host="0.0.0.0", workers=1)
