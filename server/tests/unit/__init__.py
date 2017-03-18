from tornado.httpclient import AsyncHTTPClient
from tornado.ioloop import IOLoop
from tornado.testing import AsyncHTTPTestCase

from server.models import User
from server.application import create_app
from server.tests.unit.application.test_v1_handlers import test_v1


class ModelTestBase(AsyncHTTPTestCase):
    def __init__(self, *args, **kwargs):
        super(ModelTestBase, self).__init__(*args, **kwargs)
        self.app = None
        self.db = None
        self.client = None

    def get_app(self):
        handlers = test_v1.handlers
        app = create_app(handlers, mode='testing')
        return app

    def get_new_ioloop(self):
        return IOLoop.instance()

    def reverse_url(self, name, *args, **kwargs):
        path = self.app.reverse_url(name, *args, **kwargs)
        return self.get_url(path)

    def setUp(self):
        super(ModelTestBase, self).setUp()
        self.app = self.get_app()
        self.db = self.app.db
        self.client = AsyncHTTPClient(self.io_loop)
        self.db.create_all()

    def tearDown(self):
        self.db.session.remove()
        self.db.drop_all()
        super(ModelTestBase, self).tearDown()


class ServerTestBase(ModelTestBase):
    def __init__(self, *args, **kwargs):
        super(ServerTestBase, self).__init__(*args, **kwargs)

    def setUp(self):
        super(ServerTestBase, self).setUp()
        user = User(name='john', email='john@hu.com', uuid='12345')
        password = 'cat2dog'
        user.set_password(password)
        self.db.session.add(user)
        self.db.session.commit()
