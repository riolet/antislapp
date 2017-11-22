import os
import web
import json
import pprint
import traceback
import antislapp.index
from antislapp.models.controller import Controller


class Fulfill:
    outfile = os.path.join(antislapp.index.BASE_FOLDER, 'sessions', 'test.txt')

    def __init__(self):
        pass

    @staticmethod
    def dump_error(inbound, request, outbound):
        with file(Fulfill.outfile, 'w') as f:
            f.write("\n==== error ====\n")
            er = traceback.format_exc()
            f.write(er)
            f.write("\n==== inbound ====\n")
            try:
                pprint.pprint(json.loads(inbound), f)
            except:
                f.write("(json decode failed)\n")
                pprint.pprint(inbound, f)
            f.write("\n==== translated ====\n")
            pprint.pprint(request, f)
            f.write("\n==== outbound ====\n")
            try:
                pprint.pprint(json.loads(outbound), f)
            except:
                f.write("(json decode failed)\n")
                pprint.pprint(outbound, f)
            f.write("\n==== end ====\n")

    @staticmethod
    def extract_parameters(data):
        params = data.get('result', {}).get('parameters', {})
        for key in params:
            try:
                if params[key].lower() == 'false':
                    params[key] = False
                elif params[key].lower() == 'true':
                    params[key] = True
            except:
                pass
        return params

    @staticmethod
    def extract_default_response(data):
        return data.get('result', {}).get('fulfillment', {}).get('speech', "")

    @staticmethod
    def extract_action(data):
        return data.get('result', {}).get('action', '')

    @staticmethod
    def extract_contexts(data):
        raw_contexts = data.get('result', {}).get('contexts', [])
        contexts = {}
        for ctx in raw_contexts:
            contexts[ctx['name']] = ctx
        return contexts

    @staticmethod
    def extract_resolvedQuery(data):
        return data.get('result', {}).get('resolvedQuery', '')

    def decode_inbound(self, inbound):
        try:
            data = json.loads(inbound)
        except:
            data = {}
        params = Fulfill.extract_parameters(data)
        def_response = Fulfill.extract_default_response(data)
        action = Fulfill.extract_action(data)
        query = Fulfill.extract_resolvedQuery(data)
        cid = data.get('sessionId', None)
        if cid is None:
            raise ValueError
        contexts = Fulfill.extract_contexts(data)

        request = {
            'db': antislapp.index.db,
            'params': params,
            'default': def_response,
            'action': action,
            'conversation_id': cid,
            'contexts': contexts,
            'query': query,
        }
        return request

    def process_request(self, request):
        # defence = Defence(request['db'], request['conversation_id'])
        controller = Controller(request['conversation_id'], request['default'])
        action = request['action']

        if action == "is_sued":
            controller.set_sued(request['params']['sued'], request['params'].get('name', None))
        elif action == 'get_name':
            controller.set_defendant(request['params']['name'])
        elif action == 'next_step':
            controller.set_next_step()
        elif action == 'pleas-true':
            controller.set_allegations_agree(request['params']['empty'], request['query'])
        elif action == 'pleas-false':
            controller.set_allegations_deny(request['params']['empty'], request['query'])
        elif action == 'pleas-none':
            controller.set_allegations_withhold(request['params']['empty'], request['query'])
        elif action in ('check-truth', 'check-absolute', 'check-qualified', 'check-fair', 'check-responsible'):
            controller.defence_check(request['contexts']['currentacc'], request['params'])
        elif action == 'fact':
            controller.add_fact(request['contexts']['currentacc'], request['params']['fact'])
        elif action == 'done_facts':
            controller.done_facts(request['contexts']['currentacc'])
        elif action == 'got_defamatory':
            controller.set_defamatory(request['params']['defamatory'])
        elif action == 'got_damaging':
            controller.set_damaging(request['params']['damaging'])
        elif action == 'got_apology':
            controller.set_apology(request['params'])
        elif action == 'got_court':
            controller.set_court_name(request['params']['court'])
        elif action == 'report':
            controller.report()
        elif action == 'clear_all':
            controller.reset()
        elif action == 'definition':
            controller.get_definition(request['params']['definition_terms'])
        elif action == 'antislapp':
            controller.set_antislapp(request['params']['ontario'], request['params']['ontario'])
        elif action == 'ask_boolean_answer':
            # save the answer, trigger next question or state.
            controller.boolean_answer(request['contexts']['currentacc'], request['params']['answer'])
        else:
            pass

        controller.save()
        response = controller.get_response()
        return response

    def prepare_response(self, response):
        prepared = json.dumps(response)
        return prepared

    def POST(self):
        inbound = web.data()

        request = None
        response = None
        try:
            request = self.decode_inbound(inbound)
            response = self.process_request(request)
        except Exception as e:
            traceback.print_exc()
            if request is None:
                request = 'error decoding request'
            if response is None:
                response = {
                    'speech': "error: {}".format(e),
                    'displayText': "error: {}".format(e)
                }

        outbound = self.prepare_response(response)
        self.dump_error(inbound, request, outbound)
        web.header("Content-Type", "application/json")
        return outbound
