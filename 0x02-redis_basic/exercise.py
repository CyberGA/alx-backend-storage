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


def call_history(method: Callable) -> Callable:
    """
    store the history of inputs and
    outputs for a particular function"""
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """
        wraps the decorated function and"""
        inputs = str(args)
        self._redis.rpush(method.__qualname__ + ":inputs", inputs)
        outputs = str(method(self, *args, **kwargs))
        self._redis.rpush(method.__qualname__ + ":outputs", outputs)
        return outputs
    return wrapper


def replay(fn: Callable):
    '''display the history of calls of a particular function.'''
    r = redis.Redis()
    func_name = fn.__qualname__
    c = r.get(func_name)
    try:
        c = int(c.decode("utf-8"))
    except Exception:
        c = 0
    print("{} was called {} times:".format(func_name, c))
    inputs = r.lrange("{}:inputs".format(func_name), 0, -1)
    outputs = r.lrange("{}:outputs".format(func_name), 0, -1)
    for inp, outp in zip(inputs, outputs):
        try:
            inp = inp.decode("utf-8")
        except Exception:
            inp = ""
        try:
            outp = outp.decode("utf-8")
        except Exception:
            outp = ""
        print("{}(*{}) -> {}".format(func_name, inp, outp))


class Cache:
    """declares a redis cache class"""
    def __init__(self):
        """
        store a redis client instance and
        flush the instance """
        self._redis = redis.Redis(host='localhost', port=6379, db=0)
        self._redis.flushdb()

    @count_calls
    @call_history
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
