class Route(object):
    def __init__(self, uri, view_func, methods=('GET',)):
        self.uri = uri
        self.view_func = view_func
        self.methods = list(methods)