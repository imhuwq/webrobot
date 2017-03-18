from tornado.testing import gen_test

from server.tests.unit import ServerTestBase
from server.application import create_app

from server.tests.unit.application.test_v1_handlers.main import HomePageHandler


class AppTest(ServerTestBase):
    def get_app(self):
        app = create_app(handlers=[('/', HomePageHandler)], mode='testing')
        return app

    @gen_test
    def test_app_can_start(self):
        home_page_url = self.get_url('/')
        response = yield self.client.fetch(home_page_url)
        self.assertIn(b'home page', response.body)
