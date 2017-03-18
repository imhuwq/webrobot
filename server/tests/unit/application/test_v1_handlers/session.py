import json

from tornado.gen import coroutine

from server.application import BaseHandler

from . import test_v1

session = test_v1.create_resource('session', prefix='/session')


@session.route('/')
class Session(BaseHandler):
    @coroutine
    def get(self):
        return self.write(self.session)

    @coroutine
    def post(self):
        sessions = json.loads(self.get_argument('sessions'))
        yield self.session.update(sessions)
        return self.write(self.session)

    @coroutine
    def delete(self):
        key = self.get_argument('key')
        if key in self.session:
            del self.session[key]
        return self.write(self.session)
