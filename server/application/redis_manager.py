import tornadis


class RedisManager:

    def __init__(self, app=None, session_ttl=79200):
        self.session_client = None
        self.session_ttl = session_ttl

        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        redis_config = app.redis_config
        host = redis_config.get("host") or "localhost"
        port = redis_config.get("port") or 6379
        db = redis_config.get("db") or 1
        self.session_client = tornadis.Client(
            host=host, port=port, db=db, autoconnect=True)
        app.rd = self
