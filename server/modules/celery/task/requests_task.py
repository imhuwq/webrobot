import requests


class RequestsTask:
    def __init__(self, method, url, headers=None, cookies=None, params=None, data=None):
        self.method = method
        self.url = url

        self.headers = headers or {}
        self.cookies = cookies or {}
        self.params = params or {}
        self.data = data or {}

        self.method_functions = {
            'get': self.get,
            'post': self.post
        }

    def get(self, url):
        result = requests.get(url, headers=self.headers, cookies=self.cookies, params=self.params)
        return result

    def post(self, url):
        result = requests.post(url, headers=self.headers, cookies=self.cookies, data=self.data)
        return result

    def start(self):
        method_func = self.method_functions.get(self.method, None)
        if method_func is not None:
            return method_func(self.url)
