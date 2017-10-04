import os
import web
import json
import antislapp.index
import pprint
import traceback


class Fulfill:
    outfile = os.path.join(antislapp.index.BASE_FOLDER, 'sessions', 'test.txt')

    def __init__(self):
        pass

    def dump_error(self, data):
        with file(Fulfill.outfile, 'w') as f:
            f.write("\n==== error ====\n")
            er = traceback.format_exc()
            f.write(er)
            f.write("\n==== data ====\n")
            pprint.pprint(data, f)
            f.write("\n==== end ====\n")

    def GET(self):
        web.header("Content-Type", "application/json")
        return json.dumps({'speech': 'Speech Response get', 'displayText': 'Display Text Response get'})

    def POST(self):
        data = web.data()
        try:
            raise ValueError
        except:
            self.dump_error(data)

        web.header("Content-Type", "application/json")
        return json.dumps({'speech': 'Speech Response post', 'displayText': 'Display Text Response post'})
