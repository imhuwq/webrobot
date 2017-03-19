import requests

from server.modules.celery.task.task_base import TaskBase


class RequestsTask(TaskBase):
    def __init__(self, method, target_url, headers=None, cookies=None, params=None, data=None):
        super(RequestsTask, self).__init__()
        self.method = method
        self.target_url = target_url

        self.headers = headers or {}
        self.cookies = cookies or {}
        self.params = params or {}
        self.data = data or {}

        self.method_functions = {
            'get': self.get,
            'post': self.post
        }

    def get(self):
        result = requests.get(self.target_url, headers=self.headers, cookies=self.cookies, params=self.params)
        return result

    def post(self):
        result = requests.post(self.target_url, headers=self.headers, cookies=self.cookies, data=self.data)
        return result

    def start(self):
        method_func = self.method_functions.get(self.method, None)
        if method_func is not None:
            try:
                method_func()
            except Exception:
                self.after_fail()
            else:
                self.after_success()
