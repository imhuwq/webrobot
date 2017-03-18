from tornado.gen import coroutine
from tornado.web import authenticated

from server.models import User
from server.resources.api_v1 import apiv1, BaseHandler

user = apiv1.create_resource('user', prefix='/user')


# get current user info
@user.route('/')
class UserIndex(BaseHandler):
    def get(self):
        if self.current_user:
            self.response.update({'status': 1,
                                  'name': self.current_user.name,
                                  'email': self.current_user.email,
                                  'isAnonymous': False})
        else:
            self.response.update({'status': 0,
                                  'name': 'anonymousUser',
                                  'email': 'anonymouse@example.com',
                                  'isAnonymous': True})
        return self.write(self.response)


# get user profile in detail
@user.route('/profile/')
class UserProfile(BaseHandler):
    @authenticated
    def get(self):
        return self.write('user profile')


# user login
@user.route('/login')
class UserLogin(BaseHandler):
    @coroutine
    def post(self):
        if self.current_user:
            self.response.update({'status': 0, 'msg': 'user is already logged in'})
        else:
            email = self.get_argument('email')
            password = self.get_argument('password')
            logging_user = self.query(User).filter_by(email=email).first()
            if logging_user and logging_user.authenticate(password):
                yield self.login(logging_user)
                self.response.update({'status': 1, 'msg': 'login success'})
            else:
                self.response.update({'status': -1, 'msg': 'invalid email or password'})

        return self.write(self.response)


# user logout
@user.route('/logout')
class UserLogout(BaseHandler):
    def post(self):
        if self.current_user:
            self.logout()
            self.response.update({'status': 1, 'msg': 'logout success'})
        else:
            self.response.update({'status': 0, 'msg': 'user is not logged in'})
        return self.write(self.response)


# user register
@user.route('/register')
class UserRegister(BaseHandler):
    @coroutine
    def post(self):
        if self.current_user:
            self.response.update({'status': 0, 'msg': 'user is logged in'})
        else:
            name = self.get_argument('name')
            email = self.get_argument('email')
            password = self.get_argument('password')
            name_is_valid = User.validate_name(name)
            email_is_valid = User.validate_email(email)
            password_is_valid = User.validate_password(password)

            if not all([name_is_valid, email_is_valid, password_is_valid]):
                invalid = []
                self.response.update({'status': -1, 'msg': 'invalid user info', 'invalid': invalid})
                if not name_is_valid:
                    invalid.append('name')
                if not email_is_valid:
                    invalid.append('email')
                if not password_is_valid:
                    invalid.append('password')

            else:
                existed_user = self.query(User).filter((User.name == name) | (User.email == email)).first()
                if existed_user:
                    in_use = []
                    self.response.update({'status': -2, 'msg': 'user info is in use', 'inUse': in_use})
                    if existed_user.email == email:
                        in_use.append('email')
                    if existed_user.name == name:
                        in_use.append('name')
                else:
                    new_user = User(name=name, email=email)
                    new_user.set_password(password)
                    self.db.session.add(new_user)
                    self.db.session.commit()
                    self.response.update({'status': 1, 'msg': '', 'password': password, 'name': name, 'email': email})
                    yield self.login(new_user)

        return self.write(self.response)


# change user password
@user.route('/password/change')
class UserChangePassword(BaseHandler):
    def post(self):
        if self.current_user:
            self.get_argument()
            password = self.get_argument('password')
            new_password = self.get_argument('new_password')
            if not self.current_user.authenticate(password):
                self.response.update({'status': -1, 'msg': 'incorrect current password'})
            else:
                if not User.validate_password(new_password):
                    self.response.update({'status': -1, 'msg': 'password is not secure enough'})
                else:
                    self.current_user.set_password(new_password)
                    self.db_session.commit()
                    self.response.update({'status': 1, 'msg': 'password updated successfully'})
        else:
            self.response.update({'status': 0, 'msg': 'you are not a registered user'})
        return self.write(self.response)


# user forget password
@user.route('/password/forget')
class UserForgetPassword(BaseHandler):
    def get(self):
        email_addr = self.get_argument('email')
        existed_user = self.query(User).filter_by(email=email_addr).first()
        if existed_user is not None:
            auth_token = existed_user.gen_auth_token()

            email_content = 'Someone reported that you have forgotten your password. ' \
                            'If that is true, click this link to reset your password:' \
                            ' {0}?email={1}&token={2}.' \
                            'Or you can ignore it if that is not initiated by you'. \
                format(self.reverse_url('api_v1.user.UserResetPassword'), email_addr, auth_token)

            self.send_email(receiver=email_addr, subject='Reset Password', content=email_content)

            self.response.update(
                {'status': 1,
                 'msg': 'an instruction about resetting password has been emailed to you, '
                        'check your inbox to continue'})
        else:
            self.response.update({'status': -1, 'msg': 'invalid email address'})
        return self.write(self.response)


# user reset password using token
@user.route('/password/reset')
class UserResetPassword(BaseHandler):
    def post(self):
        email = self.get_argument('email')

        existed_user = self.query(User).filter_by(email=email).first()
        if existed_user:
            token = self.get_argument('token')
            if token == user.auth_token:
                password = self.get_argument('password')
                if User.validate_password(password):
                    existed_user.set_password(password)
                    existed_user.gen_auth_token()
                    self.response.update({'status': 1, 'msg': 'password reset'})
                else:
                    self.response.update({'status': -1, 'msg': 'invalid password'})
        self.response.update({'status': 0, 'msg': 'invalid request'})
        return self.write(self.response)
