from inspect import signature
from django.core.cache import cache
from django.db.models.query import QuerySet
from django.core.handlers.wsgi import WSGIRequest

import hashlib

MAX_NUM_CHAR = 15
NONE_RESULT = "__None__"


def cache_wrapper(prefix, timeout=None):
    def arg_to_str(arg):
        if hasattr(arg, "id"):
            return str(arg.id)
        if isinstance(arg, list) or isinstance(arg, QuerySet):
            return hashlib.sha1(str(list(arg)).encode()).hexdigest()[:MAX_NUM_CHAR]
        if len(str(arg)) > MAX_NUM_CHAR:
            return str(arg)[:MAX_NUM_CHAR]
        return str(arg)

    def filter_args(args_list):
        return [x for x in args_list if not isinstance(x, WSGIRequest)]

    def get_key(func, *args, **kwargs):
        args_list = list(args)
        signature_args = list(signature(func).parameters.keys())
        args_list += [kwargs.get(k) for k in signature_args[len(args) :]]
        args_list = filter_args(args_list)
        args_list = [arg_to_str(i) for i in args_list]
        key = prefix + ":" + ":".join(args_list)
        key = key.replace(" ", "_")
        return key

    def decorator(func):
        def wrapper(*args, **kwargs):
            cache_key = get_key(func, *args, **kwargs)
            result = cache.get(cache_key)
            if result is not None:
                if result == NONE_RESULT:
                    result = None
                return result
            result = func(*args, **kwargs)
            if result is None:
                result = NONE_RESULT
            try:
                cache.set(cache_key, result, timeout)
            except:
                pass
            return result

        def dirty(*args, **kwargs):
            cache_key = get_key(func, *args, **kwargs)
            cache.delete(cache_key)

        wrapper.dirty = dirty

        return wrapper

    return decorator
