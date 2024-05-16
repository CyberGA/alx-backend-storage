#!/usr/bin/env python3
"""
web cache and tracker
"""
import requests
import redis
from functools import wraps

store = redis.Redis()


def count_url_access(method):
    """ Decorator counting how many times
    a URL is accessed """
    @wraps(method)
    def wrapper(url: str) -> str:
        # Generate keys for count and cache
        count_key = f"count:{url}"
        cached_key = f"cached:{url}"
        store.incr(count_key)

        cached_data = store.get(cached_key)

        if cached_data:
            return cached_data.decode("utf-8")

        data = method(url)
        store.setex(cached_key, 10, data)
        return data
    return wrapper


@count_url_access
def get_page(url: str) -> str:
    """ Returns HTML content of a url """
    res = requests.get(url)
    return res.text
