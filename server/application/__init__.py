from .tornado_app import Application
from .tornado_handler import BaseHandler, WSBaseHandler
from .tornado_api import API
from .redis_manager import RedisManager
from .sqlalchemy_db import DataBase

from server.instance import SETTINGS, DB_URI, TEST_DB_URI, DEVE_DB_URI


def create_app(handlers, mode='production'):
    settings = SETTINGS.copy()

    if mode == 'testing':
        settings['xsrf_cookies'] = False
        app = Application(
            handlers=handlers,
            db_uri=TEST_DB_URI,
            **settings
        )
    elif mode == 'with_xsrf':
        app = Application(
            handlers=handlers,
            db_uri=TEST_DB_URI,
            **settings
        )
    elif mode == 'develop':
        settings['debug'] = True
        app = Application(
            handlers=handlers,
            db_uri=DEVE_DB_URI,
            **settings
        )
    else:
        app = Application(
            handlers=handlers,
            db_uri=DB_URI,
            **settings
        )

    app.mode = mode

    redis = RedisManager()
    database = DataBase()

    redis.init_app(app)
    database.init_app(app)
    if mode != 'production':
        app.db.create_all()
    return app
