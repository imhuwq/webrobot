import json

from tornado.websocket import WebSocketClosedError

from server.api_v1 import apiv1, BaseHandler, WSBaseHandler

main = apiv1.create_resource('main', prefix='/main')


@apiv1.route(r'/')
class APIHome(BaseHandler):
    def get(self):
        return self.write('api page')


@main.route(r'/')
class HomePage(BaseHandler):
    def get(self, *args, **kwargs):
        return self.write('home page')


@main.route(r'/index')
class IndexPage(BaseHandler):
    def get(self):
        return self.redirect(self.reverse_url('api_v1.main.HomePage'))


@main.route(r'/xsrf')
class XsrfToken(BaseHandler):
    def get(self):
        token = self.xsrf_token
        token = token.decode()
        return self.write({'token': token})


@main.route('/chat/index')
class VideoChatDemo(WSBaseHandler):
    clients = set()

    def open(self):
        if self.current_user:
            VideoChatDemo.clients.add(self)
            super().open()
        else:
            self.write_message('WebSocket Connection Refused! Login Required.')

    def on_message(self, message):
        message = json.loads(message)
        for client in VideoChatDemo.clients:
            try:
                client.write_message(message)
                print('ok')
            except WebSocketClosedError:
                print('fail')
                client.close()
