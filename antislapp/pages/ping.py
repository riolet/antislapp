import json
import traceback
import web
import apiai
from antislapp import index
from antislapp.models.contexts import Contexts


class Ping:
    def __init__(self):
        pass

    def get_contexts(self):
        print("get contexts")
        apiai.QueryRequest('abc', 'blah', '1', 'session')

    def set_contexts(self, contexts):
        print("setting contexts")
        return "response"

    def decode_inbound(self, inbound):
        return inbound

    def process_request(self, request):
        context_model = Contexts(index.session['session_id'])
        contexts = context_model.get()
        response = context_model.set(contexts)
        return response

    def prepare_response(self, response):
        outbound = json.dumps(response)
        return outbound

    def POST(self):
        inbound = web.data()
        try:
            request = self.decode_inbound(inbound)
            response = self.process_request(request)
            outbound = self.prepare_response(response)
        except Exception as e:
            response = {
                'msg': "Error processing request: {}: {}".format(e.__class__.__name__, e),
                'trace': traceback.format_exc()
            }
            outbound = self.prepare_response(response)
        web.header("Content-Type", "application/json")
        return outbound
