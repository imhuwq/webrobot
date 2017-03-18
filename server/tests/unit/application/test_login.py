import json
from urllib.parse import urlencode

from tornado.testing import gen_test
from tornado.httpclient import HTTPRequest

from server.tests.unit import ServerTestBase


class LoginTest(ServerTestBase):
    @gen_test
    def test_01_login_is_okay(self):
        login_url = self.reverse_url('test_v1.user.UserLogin')

        body = {'email': 'john@hu.com', 'password': 'cat2dog'}
        body = urlencode(body)
        request = HTTPRequest(url=login_url, method='POST', body=body)
        response = yield self.client.fetch(request)

        body = response.body.decode()
        body = json.loads(body)

        uuid = body.get('uuid', None)
        self.assertTrue(uuid == '12345')

        body = {'email': 'joashn@hu.com', 'password': 'cat2dog'}
        body = urlencode(body)
        request = HTTPRequest(url=login_url, method='POST', body=body)
        response = yield self.client.fetch(request)

        body = response.body.decode()
        body = json.loads(body)
        uuid = body.get('uuid', None)
        self.assertTrue(uuid != '12345')

    @gen_test
    def test_02_login_state_is_okay(self):
        login_url = self.reverse_url('test_v1.user.UserLogin')
        body = {'email': 'john@hu.com', 'password': 'cat2dog'}
        body = urlencode(body)
        request = HTTPRequest(url=login_url, method='POST', body=body)
        response = yield self.client.fetch(request)

        cookie = response.headers['set-cookie']
        headers = {'cookie': cookie}

        profile_url = self.reverse_url('test_v1.user.UserProfile')
        request = HTTPRequest(url=profile_url, method='GET', headers=headers)
        response = yield self.client.fetch(request)
        body = response.body.decode()
        body = json.loads(body)

        uuid = body.get('uuid', None)
        self.assertTrue(uuid == '12345')

    @gen_test
    def test_03_logout_is_okay(self):
        login_url = self.reverse_url('test_v1.user.UserLogin')
        body = {'email': 'john@hu.com', 'password': 'cat2dog'}
        body = urlencode(body)
        request = HTTPRequest(url=login_url, method='POST', body=body)
        response = yield self.client.fetch(request)

        cookie = response.headers['set-cookie']
        headers = {'cookie': cookie}

        logout_url = self.reverse_url('test_v1.user.UserLogout')
        request = HTTPRequest(url=logout_url, method='POST', headers=headers, body='')
        response = yield self.client.fetch(request)
        body = response.body.decode()
        body = json.loads(body)

        uuid = body.get('uuid', None)
        self.assertTrue(uuid != '12345')

    @gen_test
    def test_04_logout_state_is_okay(self):
        login_url = self.reverse_url('test_v1.user.UserLogin')
        body = {'email': 'john@hu.com', 'password': 'cat2dog'}
        body = urlencode(body)
        request = HTTPRequest(url=login_url, method='POST', body=body)
        response = yield self.client.fetch(request)

        cookie = response.headers['set-cookie']
        headers = {'cookie': cookie}

        logout_url = self.reverse_url('test_v1.user.UserLogout')
        request = HTTPRequest(url=logout_url, method='POST', headers=headers, body='')
        response = yield self.client.fetch(request)
        cookie = response.headers['set-cookie']
        headers = {'cookie': cookie}

        profile_url = self.reverse_url('test_v1.user.UserProfile')
        request = HTTPRequest(url=profile_url, method='GET', headers=headers)
        response = yield self.client.fetch(request)

        body = response.body.decode()
        body = json.loads(body)

        uuid = body.get('uuid')
        self.assertTrue(uuid != '12345')
