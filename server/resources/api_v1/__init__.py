from server.application import API
from server.models import User
from server.application import BaseHandler as _BaseHandler
from server.application import WSBaseHandler as _WSBaseHandler


class BaseHandler(_BaseHandler):
    def get_current_user(self):
        return self.query(User).filter_by(uuid=self.user_uuid).first()


class WSBaseHandler(BaseHandler, _WSBaseHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


apiv1 = API(name='api_v1', prefix='/api/v1')

from .main import main
from .user import user
from .task import task
