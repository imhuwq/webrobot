from tornado.web import Application as BaseApplication


class Application(BaseApplication):
    def __init__(self, *args, db_uri=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.db = None
        self.db_uri = db_uri
        self.rd = None

        self.mode = 'production'
