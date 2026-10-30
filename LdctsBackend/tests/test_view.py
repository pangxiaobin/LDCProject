#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : test_view.py
import pytest
from httpx import AsyncClient

from models.base import User


@pytest.mark.anyio
async def test_admin_get_user(client_with_admin_token: AsyncClient):
    response = await client_with_admin_token.get("/api/users")
    assert response.status_code == 200


@pytest.mark.anyio
async def test_normal_get_users(client_with_norm_token: AsyncClient):
    response = await client_with_norm_token.get("/api/users")
    assert response.status_code == 403
