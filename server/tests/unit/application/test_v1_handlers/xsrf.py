from server.application import BaseHandler

from . import test_v1

xsrf = test_v1.create_resource('xsrf', prefix='/xsrf')


@xsrf.route('/')
class XsrfToken(BaseHandler):
    def get(self):
        xsrf = self.xsrf_token
        xsrf = xsrf.decode()
        return self.write({'xsrf': xsrf})

    def post(self):
        return self.write({'msg': 'ok'})
