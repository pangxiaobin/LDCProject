#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : middleware.py


import asyncio
import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from common.utils import check_re_match_url, get_client_ip
from conf import settings
from core.security import parse_access_token
