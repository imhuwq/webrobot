import uuid
import json

from functools import wraps

from tornado.gen import coroutine
from tornado.web import RequestHandler, MissingArgumentError, Finish
from tornado.websocket import WebSocketHandler

from server.application.redis_session import Session
from server.application.sqlalchemy_db import UserBase

from server.extentions import Email


class Argument:
    def __init__(self, name, type_=str, default=None):
        self.name = name
        self.type_ = type_

        if default is not None:
            if not isinstance(default, type_):
                raise ValueError("default value is not of the required type")
        self.default = default


def login_required(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if not self.current_user:
            self.raise_error(403, 0, msg='please login')
        return func(self, *args, **kwargs)

    return wrapper


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
        return self.query(UserBase).filter_by(uuid=self.user_uuid).first()

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

    def raise_error(self, code, status=-1, msg='fail', **kwargs):
        self.set_status(code)
        self.response.update({'status': status, 'msg': msg})
        self.response.update(kwargs)
        self.write(self.response)
        self.finish()
        raise Finish()

    def start_response(self, status=1, msg='ok', **kwargs):
        self.response.update({'status': status, 'msg': msg})
        self.response.update(kwargs)
        self.write(self.response)
        self.finish()
        raise Finish()

    def parse_arguments(self, required_arguments):
        argument_values = []
        for argument in required_arguments:
            try:
                if argument.default is not None:
                    value = self.get_argument(argument.name, default=argument.default)
                else:
                    value = self.get_argument(argument.name)

                if isinstance(value, str) and argument.type_ != str:
                    value = json.loads(value)
                    if not isinstance(value, argument.type_):
                        msg = '%s<%r> cannot be converted to type %s' % (argument.name, value, argument.type_)
                        raise TypeError(msg)
            except MissingArgumentError:
                self.raise_error(400, -1, msg='%s is required' % argument.name)
            except TypeError as e:
                msg = str(e)
                self.raise_error(400, -1, msg=msg)
            else:
                argument_values.append(value)
        return argument_values

    def data_received(self, chunk):
        """Implement this method to handle streamed request data.

        Requires the `.stream_request_body` decorator.
        """
        pass


class WSBaseHandler(BaseHandler, WebSocketHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def check_origin(self, origin):
        return True

    def open(self):
        self.write_message('WebSocket Connected!')

    def data_received(self, chunk):
        """Implement this method to handle streamed request data.

        Requires the `.stream_request_body` decorator.
        """
        pass

    def on_message(self, message):
        """Handle incoming messages on the WebSocket

        This method must be overridden.
        """
        raise NotImplementedError
