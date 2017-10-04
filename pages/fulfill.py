import web
import json


class Fulfill:
    def __init__(self):
        pass

    def GET(self):
        web.header("Content-Type", "application/json")
        return json.dumps({'speech': 'Speech Response get', 'displayText': 'Display Text Response get'})

    def POST(self):
        web.header("Content-Type", "application/json")
        return json.dumps({'speech': 'Speech Response post', 'displayText': 'Display Text Response post'})
