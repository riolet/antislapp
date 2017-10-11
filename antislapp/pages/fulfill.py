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

    @staticmethod
    def extract_parameters(data):
        return data.get('result', {}).get('parameters', {})


    def POST(self):
        raw_data = web.data()
        try:
            raise ValueError
        except:
            self.dump_error(raw_data)

        data = json.loads(raw_data)
        params = Fulfill.extract_parameters(data)
        program = params.get('programs')
        if program == 'hangman':
            followupEvent = {'name': 'starthangman', 'data':{}}
        elif program == 'lamprepair':
            followupEvent = {'name': 'startlamp', 'data':{}}
        else:
            followupEvent = {'name': 'startoops', 'data':{}}

        response = {
            'speech': 'Speech Response post',  # String. Response to the request.
            'displayText': 'Display Text Response post',  # String. Text displayed by client.
            'data': '',  # Object. this data is passed through DialogFlow and sent to the client.
            'contextOut': [],  # Array of context objects. Output context for the current intent.
            # eg: [{"name":"weather", "lifespan":2, "parameters":{"city":"Rome"}}]
            'source': '',  # String. Data source (??)
            'followupEvent': {}  # Object. Event name and optional parameters sent from the web service to Dialogflow.
            # eg: {"name":"<event_name>","data":{"<parameter_name>":"<parameter_value>"}}
        }

        response['followupEvent'] = followupEvent

        web.header("Content-Type", "application/json")
        return json.dumps(response)
