from server.application import API

test_v1 = API(name='test_v1', prefix='/test/v1')

from .session import session
from .user import user
from .xsrf import xsrf
from .email import email
