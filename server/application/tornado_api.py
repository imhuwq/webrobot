class API:
    def __init__(self, name, prefix):
        self.name = name

        if not prefix.endswith('/'):
            prefix += '/'
        self.prefix = prefix

        self.handlers = []

        self.resources = []

    def route(self, path, kwargs=None, name=None):
        if path.startswith('/'):
            path = path[1:]
        path = '{0}{1}'.format(self.prefix, path)

        def handler_wrapper(handler):
            self.handlers.append((path, handler, kwargs, name))

            return handler

        return handler_wrapper

    def route_handler(self, path, handler, kwargs=None, name=None):
        if self.prefix:
            if path.startswith('/'):
                path = path[1:]
            path = '{0}{1}'.format(self.prefix, path)

        self.handlers.append((path, handler, kwargs, name))

    def create_resource(self, name, prefix):
        name = '{0}.{1}'.format(self.name, name)
        resource = _Resource(name, prefix, self)
        self.resources.append(resource)
        return resource


class _Resource:
    def __init__(self, name, prefix, api):
        self.name = name
        self.api = api

        if not prefix.endswith('/'):
            prefix += '/'
        self.prefix = prefix

        self.route_records = []

    def route(self, path, kwargs=None, name=None):
        prefix = self.prefix

        if path.startswith('/'):
            path = path[1:]
        path = '{0}{1}'.format(prefix, path)

        def handler_wrapper(handler):
            if name is None:
                handler_name = '{0}.{1}'.format(self.name, handler.__name__)
            else:
                handler_name = name
            self.api.route_handler(path, handler, kwargs=kwargs, name=handler_name)

            return handler

        return handler_wrapper
