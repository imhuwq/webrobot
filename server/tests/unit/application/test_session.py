import json
import time

from tornado.gen import coroutine
from tornado.testing import gen_test
from tornado.httpclient import HTTPRequest
from tornado.httputil import url_concat, urlencode

from server.tests.unit import ServerTestBase


class SessionTest(ServerTestBase):
    def setUp(self):
        super(SessionTest, self).setUp()
        self.target = self.reverse_url('test_v1.session.Session')

    @coroutine
    def get_cookie(self):
        request = HTTPRequest(url=self.target, method='GET')
        response = yield self.client.fetch(request)

        cookie = response.headers['set-cookie']

        return cookie

    @gen_test
    def test_01_access_session(self):
        response = yield self.client.fetch(self.target)
        response = json.loads(response.body.decode())
        self.assertEqual(response, {})

    @gen_test
    def test_02_write_session(self):
        sessions = json.dumps({"msg": "session_ok"})
        body = urlencode({"sessions": sessions})
        request = HTTPRequest(url=self.target, method='POST', body=body)
        response = yield self.client.fetch(request)
        response = json.loads(response.body.decode())
        msg = response.get('msg')
        self.assertEqual(msg, 'session_ok')

    @gen_test
    def test_03_save_session(self):
        cookie = yield self.get_cookie()
        headers = {'cookie': cookie}
        sessions = json.dumps({"msg": "session is saved"})
        body = urlencode({"sessions": sessions})
        request = HTTPRequest(url=self.target, method='POST', body=body, headers=headers)
        yield self.client.fetch(request)

        request = HTTPRequest(url=self.target, method='GET', headers=headers)
        response = yield self.client.fetch(request)
        response = json.loads(response.body.decode())
        msg = response.get('msg')

        self.assertEqual(msg, 'session is saved')

    @gen_test
    def test_04_edit_session(self):
        cookie = yield self.get_cookie()
        headers = {'cookie': cookie}

        created_time = time.time()
        sessions = {'msg': 'session is created', 'time': created_time}
        sessions = json.dumps(sessions)
        body = urlencode({'sessions': sessions})
        request = HTTPRequest(url=self.target, method='POST', body=body, headers=headers)
        yield self.client.fetch(request)

        sessions = {'msg': 'session is edited'}
        sessions = json.dumps(sessions)
        body = urlencode({'sessions': sessions})
        request = HTTPRequest(url=self.target, method='POST', body=body, headers=headers)
        yield self.client.fetch(request)

        request = HTTPRequest(url=self.target, method='GET', headers=headers)
        response = yield self.client.fetch(request)
        response = json.loads(response.body.decode())

        self.assertEqual(response, {'msg': 'session is edited', 'time': created_time})

    @gen_test
    def test_05_delete_session(self):
        cookie = yield self.get_cookie()
        headers = {'cookie': cookie}

        created_time = time.time()
        sessions = {'msg': 'session is created', 'time': created_time}
        sessions = json.dumps(sessions)
        body = urlencode({'sessions': sessions})
        request = HTTPRequest(url=self.target, method='POST', body=body, headers=headers)
        yield self.client.fetch(request)

        url = url_concat(self.target, {'key': 'msg'})
        request = HTTPRequest(url=url, method='DELETE', headers=headers)
        yield self.client.fetch(request)

        request = HTTPRequest(url=self.target, method='GET', headers=headers)
        response = yield self.client.fetch(request)
        response = json.loads(response.body.decode())

        self.assertEqual(response, {'time': created_time})

    @gen_test
    def test_06_login_session(self):
        cookie = yield self.get_cookie()
        headers = {'cookie': cookie}

        created_time = time.time()
        body = urlencode({'sessions': json.dumps({'msg': 'session is created', 'time': created_time})})
        request = HTTPRequest(url=self.target, method='POST', headers=headers, body=body)
        yield self.client.fetch(request)

        login_url = self.reverse_url('test_v1.user.UserLogin')
        body = urlencode({'email': 'john@hu.com', 'password': 'cat2dog'})
        request = HTTPRequest(url=login_url, method='POST', headers=headers, body=body)
        response = yield self.client.fetch(request)

        cookie = response.headers['set-cookie']
        headers = {'cookie': cookie}

        body = json.loads(response.body.decode())
        self.assertEqual(body.get('uuid'), '12345')

        request = HTTPRequest(url=self.target, method='GET', headers=headers)
        response = yield self.client.fetch(request)
        response = json.loads(response.body.decode())
        self.assertEqual(response, {'msg': 'session is created', 'time': created_time})
