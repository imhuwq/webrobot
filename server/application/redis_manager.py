import tornadis


class RedisManager:
    def __init__(self, app=None, session_ttl=79200):
        self.session_client = tornadis.Client(host="localhost", port=6379, db=1, autoconnect=True)

        self.session_ttl = session_ttl

        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.rd = self

