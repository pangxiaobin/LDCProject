#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : log.py

"""
日志存储服务
"""
import os
import sys
from pathlib import Path

from loguru import logger

from conf import settings

LOG = settings.LOG
# Add log storage file  添加日志存储路径
SERVER_PATH = Path(__file__).resolve().parent.parent
LOG_PATH = f"{SERVER_PATH}/logs"
LOG_SIZE = LOG.get("max_log_size")
LOG_BACKUP_COUNT = LOG.get("backup_count")

USE_COLOR = settings.DEBUG


def setup(log_name):
    logger.remove()

    _format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss:SSS}</> | "
        "<lvl>{level}</> | <cyan>{file}:{line}</> - <lvl>{function}: {message}</> "
    )
    logger.add(
        sys.stderr,
        level="DEBUG",
        colorize=USE_COLOR,
        enqueue=True,
        diagnose=False,
        format=_format,
    )

    params = {
        "rotation": LOG_SIZE,
        "retention": LOG_BACKUP_COUNT,
        "compression": "zip",
        "encoding": "utf8",
        "enqueue": True,
        "format": _format,
    }

    logger.add(os.path.join(LOG_PATH, f"{log_name}_debug.log"), level="DEBUG", **params)

    logger.add(os.path.join(LOG_PATH, f"{log_name}_error.log"), level="ERROR", **params)


logger.setup = setup
logger: logger


def demo():
    logger.debug("debug message")
    logger.info("info level message")
    logger.warning("warning level message")
    logger.critical("critical level message")
    logger.error("error level message")
    logger.success("success level message")


if __name__ == "__main__":
    setup("server")
    demo()
