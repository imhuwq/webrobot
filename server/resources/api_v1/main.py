from server.resources.api_v1 import apiv1, BaseHandler

main = apiv1.create_resource('main', prefix='/main')


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
