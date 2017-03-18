from server.application import BaseHandler


class HomePageHandler(BaseHandler):
    def get(self):
        return self.write('home page')
