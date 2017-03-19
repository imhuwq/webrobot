from functools import wraps

TASKS_MAP = {}


def register_task(task_class):
    TASKS_MAP.setdefault(task_class.name, task_class)

    @wraps(task_class)
    def wrapper(*args, **kwargs):
        return task_class(*args, **kwargs)

    return wrapper


class TaskBase:
    def __init__(self):
        pass

    def start(self):
        raise NotImplementedError

    def after_success(self):
        pass

    def after_fail(self):
        pass
