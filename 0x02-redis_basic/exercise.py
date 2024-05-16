#!/usr/bin/env python3
"""Module for a redis class and methods"""
import redis
from typing import Union
from uuid import uuid4


class Cache:
    """declares a redis cache class"""
    def __init__(self):
        """
        store a redis client instance and
        flush the instance """
        self._redis = redis.Redis(host='localhost', port=6379, db=0)
        self._redis.flushdb()

    def store(self, data: Union[str, bytes, int, float]) -> str:
        """takes a data arg and
        returns the key after storing it"""
        stored_key = str(uuid4())
        self._redis.set(stored_key, data)
        return stored_key
