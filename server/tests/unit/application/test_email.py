from tornado.testing import gen_test

from server.tests.unit import ServerTestBase


class EmailTest(ServerTestBase):
    @gen_test
    def test_01_send_email(self):
        send_email_page = self.reverse_url('test_v1.email.SendEmail')
        response = yield self.client.fetch(send_email_page)
        self.assertIn(b'email sent', response.body)
