#!/usr/bin/env python3
"""Module for a redis class and methods"""
import redis
from typing import Union, Callable, Optional
from uuid import uuid4
from functools import wraps


def count_calls(method: Callable) -> Callable:
    """
    count how many times methods of the Cache class are called.
    """
    key = method.__qualname__

    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """
        wraps the decorated function and
        return the wrapper"""
        self._redis.incr(key)
        return method(self, *args, **kwargs)
    return wrapper


class Cache:
    """declares a redis cache class"""
    def __init__(self):
        """
        store a redis client instance and
        flush the instance """
        self._redis = redis.Redis(host='localhost', port=6379, db=0)
        self._redis.flushdb()

    @count_calls
    def store(self, data: Union[str, bytes, int, float]) -> str:
        """takes a data arg and
        returns the key after storing it"""
        stored_key = str(uuid4())
        self._redis.set(stored_key, data)
        return stored_key

    def get(self, key: str,
            fn: Optional[Callable] = None) -> Union[str, bytes, int, float]:
        """
        converts the data to desired format"""
        val = self._redis.get(key)
        if fn:
            val = fn(val)
        return val

    def get_str(self, key: str) -> str:
        """parametrize Cache.get with the correct conversion function"""
        return self.get(key, fn=lambda x: x.decode("utf-8"))

    def get_int(self, key: str) -> int:
        """parametrize Cache.get with the correct conversion function"""
        try:
            return self.get(key, fn=lambda x: int(x.decode("utf-8")))
        except Exception:
            return 0
