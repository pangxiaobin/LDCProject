#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : test_security.py

from core.security import verify_password, get_password_hash


def test_verify_password():
    hashed_password = get_password_hash("password123")
    assert verify_password("password123", hashed_password)
    assert verify_password("wrongpassword", hashed_password) == False


def test_get_password_hash():
    password = "password123"
    hashed_password = get_password_hash(password)
    assert hashed_password != password
    assert verify_password(password, hashed_password)
