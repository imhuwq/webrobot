from functools import wraps

from celery import chord
from enum import Enum

from server.modules.celery import celery_app
from server.modules.celery.task.task_base import register_task, TASKS_MAP
from server.modules.celery.task.requests_task import RequestsTask


class TaskTypes(Enum):
    TASK_INITIALIZER = "celery_task_initializer"
    HTTP_REQUEST_REQUESTS_GET = "http_request.requests.get"
    CONSOLE_NOTIFIER_PYTHON_PRINT = "console_notifier.python.print"


@celery_app.task(name="celery_task_initializer")
def init_task(*args, **kwargs):
    chord_tasks = kwargs.get("chords", [])

    chords = []
    for task in chord_tasks:
        task_name = task.get("task")
        task_class = TASKS_MAP.get(task_name)
        task_args = task.get("args")
        task_kwargs = task.get("kwargs")
        chords.append(task_class.s(*task_args, **task_kwargs))

    callback = kwargs.get("callback", None)
    if callback is not None:
        callback_task = callback.get("task")
        callback_task_class = TASKS_MAP.get(callback_task)
        task_args = callback.get("args")
        task_kwargs = callback.get("kwargs")
        callback = callback_task_class.s(*task_args, **task_kwargs)
    chord(chords)(callback)


@register_task
@celery_app.task(name=TaskTypes.HTTP_REQUEST_REQUESTS_GET)
def requests_get(*args, **kwargs):
    url = kwargs.get("url")
    headers = kwargs.get("headers")
    cookies = kwargs.get("cookies")
    params = kwargs.get("params")
    data = kwargs.get("data")
    RequestsTask("get", url, headers=headers, cookies=cookies, params=params, data=data)


@register_task
@celery_app.task(name=TaskTypes.CONSOLE_NOTIFIER_PYTHON_PRINT)
def python_print(*args, **kwargs):
    msg = kwargs.get("msg")
    print("msg: %s" % msg)


def validate_tasks(tasks):
    for task in tasks:
        status, msg = validate_task(task)
        if status is False:
            return status, msg
    return True, "ok"


def validate_task(task):
    type_ = task.get("type", None)
    if type_ is None:
        return False, "task type is unknown"
    else:
        validator = VALIDATOR_MAP.get(type_, None)
        if validator is None:
            return False, "task validation fail"
        else:
            return validator(task)


VALIDATOR_MAP = {}


def register_validator(task_type):
    def decorator(func):
        if VALIDATOR_MAP.get(task_type):
            raise Exception("validator is registered already")
        else:
            VALIDATOR_MAP[task_type] = func

        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    return decorator


def validate_interval(period):
    every = period.get("every", None)
    if every is None:
        return False, "every is required for interval task"

    unit = period.get("unit", None)
    if unit is None:
        return False, "unit is required for interval task"
    return True, "ok"


def validate_crontab(period):
    minute = period.get("minute", None)
    if minute is None:
        return False, "minute is required for crontab task"

    hour = period.get("hour", None)
    if hour is None:
        return False, "hour is required for crontab task"

    day_of_week = period.get("day_of_week", None)
    if day_of_week is None:
        return False, "day_of_week is required for crontab task"

    day_of_month = period.get("day_of_month", None)
    if day_of_month is None:
        return False, "day_of_month is required for crontab task"

    month_of_year = period.get("month_of_year", None)
    if month_of_year is None:
        return False, "month_of_year is required for crontab task"

    return True, "ok"


@register_validator(TaskTypes.TASK_INITIALIZER.value)
def validate_initializer(task):
    period = task.get("period", None)
    method = period.get("method", None)

    if method not in ["interval", "crontab"]:
        return False, "period task method is not supported, choose from interval or crontab"

    if method == "interval":
        return validate_interval(period)
    elif method == "crontab":
        return validate_crontab(period)


@register_validator(TaskTypes.HTTP_REQUEST_REQUESTS_GET.value)
def validate_requests_get(task):
    kwargs = task.get("kwargs", {})
    url = kwargs.get("url", None)
    if url is None:
        return False, "url is missing for task type: %s" % task.get("type")
    return True, "ok"


@register_validator(TaskTypes.CONSOLE_NOTIFIER_PYTHON_PRINT.value)
def validate_python_print(task):
    kwargs = task.get("kwargs", {})
    msg = kwargs.get("msg", None)
    if msg is None:
        return False, "msg is missing"
    return True, "ok"
