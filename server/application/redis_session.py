import json

from tornado.gen import coroutine


class Session(dict):
    def __init__(self, handler):
        super(Session, self).__init__()
        self.handler = handler
        self.client = handler.application.rd.session_client
        self.default_ttl = handler.application.rd.session_ttl

        self.key = None

    @coroutine
    def prepare(self):
        self.key = 'session_%s' % self.handler.user_uuid
        yield self.get_all()

    @coroutine
    def get_all(self):
        session = yield self.client.call("get", self.key)
        if session:
            session = json.loads(session.decode())
        else:
            session = {}
        self.update(session)

    @coroutine
    def update_redis(self):
        yield self.client.call("set", self.key, json.dumps(self), 'ex', self.default_ttl)

    @coroutine
    def rename(self, new_key):
        session = yield self.client.call('get', self.key)
        if session:
            new_key = 'session_%s' % new_key
            yield self.client.call('rename', self.key, new_key)
            self.key = new_key

    @coroutine
    def clear(self):
        super(Session, self).clear()
        yield self.update_redis()

    @coroutine
    def __getitem__(self, item):
        super(Session, self).__getitem__(item)

    @coroutine
    def __setitem__(self, key, value):
        super(Session, self).__setitem__(key, value)
        yield self.update_redis()

    @coroutine
    def __delitem__(self, key):
        super(Session, self).__delitem__(key)
        yield self.update_redis()

    @coroutine
    def update(self, E=None, **F):
        super(Session, self).update(E, **F)
        yield self.update_redis()
