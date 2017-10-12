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
            try:
                pprint.pprint(json.loads(data), f)
            except:
                print("(json decode failed)")
                pprint.pprint(data, f)
            f.write("\n==== end ====\n")

    @staticmethod
    def extract_parameters(data):
        return data.get('result', {}).get('parameters', {})

    @staticmethod
    def extract_default_response(data):
        return data.get('result', {}).get('fulfillment', {}).get('speech', "")

    def POST(self):
        raw_data = web.data()
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

        try:
            data = json.loads(raw_data)
            params = Fulfill.extract_parameters(data)
            def_response = Fulfill.extract_default_response(data)
            response_text = "default: {0}, params: {1}".format(repr(def_response), repr(params))
            response['displayText'] = response_text
        except:
            pass

        self.dump_error(raw_data)

        web.header("Content-Type", "application/json")
        return json.dumps(response)
