#!/usr/bin/env python3
"""
web cache and tracker
"""
import requests
import redis
from functools import wraps

store = redis.Redis(host='localhost', port=6379, db=0)


def cacher(method):
    """ Decorator counting how many times
    a URL is accessed """
    @wraps(method)
    def wrapper(url):
        cached_key = "cached:" + url
        count_key = "count:" + url
        store.incr(count_key)
        cached_data = store.get(cached_key)
        if cached_data:
            return cached_data.decode("utf-8")

        content = method(url)

        store.setex(cached_key, 10, content)
        return content
    return wrapper


@cacher
def get_page(url: str) -> str:
    """ Returns HTML content of a url """
    res = requests.get(url)
    return res.text
