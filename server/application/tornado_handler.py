import uuid

from tornado.gen import coroutine
from tornado.web import RequestHandler
from tornado.websocket import WebSocketHandler

from server.application.redis_session import Session
from server.application.sqlalchemy_db import User

from server.extentions import Email


class BaseHandler(RequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.db = self.application.db
        self.query = self.application.db.session.query
        self.db_session = self.application.db.session
        self.session = Session(self)
        self.user_uuid = None

        self.response = {'status': 0, 'msg': ''}

    @coroutine
    def prepare(self):
        user_uuid = self.get_secure_cookie("user_uuid")
        if user_uuid:
            self.user_uuid = user_uuid.decode()
            self.current_user = self.get_current_user()
        else:
            self.set_random_user_cookie()

        yield self.session.prepare()

    def set_random_user_cookie(self):
        self.user_uuid = uuid.uuid4().hex
        self.set_secure_cookie("user_uuid", self.user_uuid)

    def get_current_user(self):
        return self.query(User).filter_by(uuid=self.user_uuid).first()

    @coroutine
    def login(self, user):
        if not self.current_user:
            yield self.session.rename(user.uuid)
            self.current_user = user
            self.user_uuid = user.uuid
            self.set_secure_cookie("user_uuid", self.user_uuid)

    def logout(self):
        if self.current_user:
            self.set_random_user_cookie()

    def send_email(self, receiver, subject, content):
        mailer = Email(self.application)
        mailer.write(receiver, subject, content)
        mailer.send()


class WSBaseHandler(BaseHandler, WebSocketHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def check_origin(self, origin):
        return True

    def open(self):
        self.write_message('WebSocket Connected!')
