from functools import wraps
from server.modules.celery.task.tasks import TaskTypes


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


@register_validator(TaskTypes.TASK_TRIGGER.value)
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
