import uuid
from functools import wraps


def gen_uuid():
    return uuid.uuid4().hex


def silent_return_none(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            rv = func(*args, **kwargs)
        except Exception:
            rv = None
        return rv

    return wrapper
