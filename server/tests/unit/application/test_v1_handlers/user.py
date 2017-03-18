from tornado.gen import coroutine

from server.models import User
from server.application import BaseHandler

from . import test_v1

user = test_v1.create_resource('user', prefix='/user')


@user.route('/login')
class UserLogin(BaseHandler):
    @coroutine
    def post(self):
        email = self.get_argument('email')
        if email:
            user = self.query(User).filter_by(email=email).first()
            if user:
                password = self.get_argument('password')
                if user.authenticate(password):
                    yield self.login(user)
        return self.write({'uuid': self.user_uuid})


@user.route('/logout')
class UserLogout(BaseHandler):
    @coroutine
    def post(self):
        self.logout()
        self.write({'uuid': self.user_uuid})


@user.route('/profile')
class UserProfile(BaseHandler):
    @coroutine
    def get(self):
        return self.write({'uuid': self.user_uuid})


@user.route('/(?P<city>[^\/]*)/fans')
class FansOfCity(BaseHandler):
    def get(self, city):
        return self.write(city)
