import json
import web
import traceback
from antislapp.models import dialogue
from antislapp import index


class Converse():
    def __init__(self):
        pass

    def decode_inbound(self, inbound):
        data = json.loads(inbound)
        request = {
            'msg': data['msg']
        }
        return request

    def process_request(self, request):
        d = dialogue.Dialogue(index.session['session_id'], index.db)
        response = d.send_message(request['msg'])
        answer = {
            'msg': response.get_speech(),
            'data': response.get_data()
        }
        return answer

    def prepare_response(self, response):
        outbound = json.dumps(response)
        return outbound

    def GET(self):
        return self.POST()

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
