import web
from antislapp import index


class Home:
    def __init__(self):
        pass

    def GET(self):
        return index.render.home()