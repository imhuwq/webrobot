from celery import chord
from enum import Enum

from server.modules.celery import celery_app
from server.modules.celery.task.task_base import register_task, TASKS_MAP
from server.modules.celery.task.requests_task import RequestsTask


class TaskTypes(Enum):
    HTTP_REQUEST_REQUESTS_GET = 'http_request.requests.get'
    CONSOLE_NOTIFIER_PYTHON_PRINT = 'console_notifier.python.print'


@celery_app.task(name=TaskTypes.HTTP_REQUEST_REQUESTS_GET)
def init_task(*args, **kwargs):
    chord_tasks = kwargs.get("chords", [])

    chords = []
    for task in chord_tasks:
        task_name = task.get('task')
        task_class = TASKS_MAP.get(task_name)
        task_args = task.get('args')
        task_kwargs = task.get('kwargs')
        chords.append(task_class.s(*task_args, **task_kwargs))

    callback = kwargs.get('callback', None)
    if callback is not None:
        callback_task = callback.get('task')
        callback_task_class = TASKS_MAP.get(callback_task)
        task_args = callback.get('args')
        task_kwargs = callback.get('kwargs')
        callback = callback_task_class.s(*task_args, **task_kwargs)
    chord(chords)(callback)


@register_task
@celery_app.task(name='http_request.requests.get')
def requests_get(*args, **kwargs):
    url = kwargs.get("url")
    headers = kwargs.get("headers")
    cookies = kwargs.get("cookies")
    params = kwargs.get("params")
    data = kwargs.get("data")
    RequestsTask('get', url, headers=headers, cookies=cookies, params=params, data=data)


@register_task
@celery_app.task(name=TaskTypes.CONSOLE_NOTIFIER_PYTHON_PRINT)
def python_print(*args, **kwargs):
    msg = kwargs.get("msg")
    print("msg: %s" % msg)
