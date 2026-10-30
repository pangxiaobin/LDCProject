#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : shell.py
import asyncio
from pathlib import Path
import sys

from tortoise import Tortoise

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from db.database import do_stuff


def run_async(coro):
    # 获取或创建事件循环并运行异步代码
    loop = asyncio.get_event_loop()
    if loop.is_running():
        # 如果事件循环已经运行，则创建一个新的事件循环
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)


def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(do_stuff())

    # 导入ptpython的repl功能
    from ptpython.repl import embed

    # 启动ptpython的REPL，传递当前的globals()，这样可以在REPL中使用全局变量
    embed(globals(), locals())

    # 当REPL关闭时，执行Tortoise ORM的关闭连接操作
    loop.run_until_complete(Tortoise.close_connections())


if __name__ == "__main__":
    main()
