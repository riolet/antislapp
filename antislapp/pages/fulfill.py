import os
import web
import json
import pprint
import traceback
import antislapp.index
from antislapp.models.defence import Defence


class Fulfill:
    outfile = os.path.join(antislapp.index.BASE_FOLDER, 'sessions', 'test.txt')

    def __init__(self):
        self.defence_triggers = {
            'Truth': 'trigger-truth',
            'Absolute Privilege': 'trigger-absolute',
            'Qualified Privilege': 'trigger-qualified',
            'Fair Comment': 'trigger-fair',
            'Responsible Communication': 'trigger-responsible'
        }

    def dump_error(self, inbound, request, outbound):
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
            pprint.pprint(request)
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
            if params[key].lower() == 'false':
                params[key] = False
            elif params[key].lower() == 'true':
                params[key] = True
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
            contexts[ctx['name']] = ctx['parameters']
            if 'lifespan' not in contexts[ctx['name']]:
                contexts[ctx['name']]['lifespan'] = ctx['lifespan']
        return contexts

    @staticmethod
    def join_list(items):
        l = len(items)
        if l == 0:
            joined = ''
        elif l == 1:
            joined = items[0]
        elif l == 2:
            joined = "{} and {}".format(*items)
        else:
            joined = "{}, and {}".format(", ".join(items[:-1]), items[-1])
        return joined

    @staticmethod
    def summarize(params):
        if params.get('sued', False):
            sued = 'you have been sued'
        else:
            sued = "you have not been sued"

        if params.get('truth', False):
            if params.get('truth-evidence'):
                truth = "your words were true and you have some proof"
            else:
                truth = "your words were true but you have no proof"
        else:
            truth = "your words were untrue"

        if 'absolute' in params:
            if params['absolute']:
                if params.get('abspriv', False):
                    absolute = 'you were in a position of absolute privilege'
                else:
                    absolute = 'you were in a position of privilege but repeated yourself after the privilege ended'
            else:
                absolute = "you weren't in a position of absolute privilege"
        else:
            absolute = None

        if 'qualified' in params:
            if params['qualified']:
                qualified = 'you were in a position of qualified privilege'
            else:
                qualified = "you weren't in a position of qualified privilege"
        else:
            qualified = None

        if 'comment' in params:
            if params['comment']:
                comment = 'you were expressing your opinion on a matter of public interest'
            else:
                comment = "it didn't qualify as fair comment"
        else:
            comment = None

        if 'journalist' in params:
            if params['journalist']:
                journalist = 'you were commenting on an urgent matter of public interest'
            else:
                journalist = 'you didn\'t qualify for "Responsible Communication" defence.'
        else:
            journalist = None

        points = [sued, truth, absolute, qualified, comment, journalist]
        points = [p for p in points if p]
        summary = "So, to summarize: {}".format(Fulfill.join_list(points))
        return summary

    def decode_inbound(self, inbound):
        try:
            data = json.loads(inbound)
        except:
            data = {}
        params = Fulfill.extract_parameters(data)
        def_response = Fulfill.extract_default_response(data)
        action = Fulfill.extract_action(data)
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
            'contexts': contexts
        }
        return request

    def process_request(self, request):
        defence = Defence(request['db'], request['conversation_id'])

        response = {
            'speech': request['default'],
            'displayText': request['default'],
            #'event': {"name":"<event_name>","data":{"<parameter_name>":"<parameter_value>"}},
            #'data': _,
            #'contextOut': [{"name":"weather", "lifespan":2, "parameters":{"city":"Rome"}}],
            # context name must be lowercase
            'source': 'riobot',
        }

        if request['action'] == "is_sued":
            defence.set_sued(request['params']['sued'])
        elif request['action'] == 'get_accusations':
            defence.add_accusation(request['params']['reason'])
        elif request['action'] == 'done_accusations':
            next = defence.determine_next_defence()
            # next has .acc_id, .acc, .def OR is None
            if next is None:
                response['followupEvent'] = {'name': 'trigger-report', 'data': {}}
            else:
                response['contextOut'] = [{
                    'name': 'currentacc',
                    'lifespan': 2,
                    'parameters': next
                }]
                response['followupEvent'] = {
                    'name': self.defence_triggers[next['def']],
                    'data': {}
                }
            del response['speech']  # required to be absent
            del response['displayText']  # required to be absent
        elif request['action'] in ('check-truth', 'check-absolute', 'check-qualified', 'check-fair', 'check-responsible'):
            # store the new defence data received.
            # TODO: lots of assumptions here. How can we mitigate / strengthen?
            update = request['contexts']['currentacc']
            defence.add_defence(update['acc_id'], update['def'], request['params']['valid'])

            next = defence.determine_next_defence()
            # next has .acc_id, .acc, .def OR is None
            if next is None:
                response['followupEvent'] = {'name': 'trigger-report', 'data': {}}
            else:
                response['contextOut'] = [{
                    'name': 'currentacc',
                    'lifespan': 2,
                    'parameters': next
                }]
                response['followupEvent'] = {
                    'name': self.defence_triggers[next['def']],
                    'data': {}
                }
            del response['speech']  # required to be absent
            del response['displayText']  # required to be absent
        elif request['action'] == 'report':
            report = defence.report()
            response['speech'] = report
            response['displayText'] = report
        elif request['action'] == 'clear_all':
            defence.reset()
        else:
            pass

        defence.save()
        return response

    def prepare_response(self, response):
        prepared = json.dumps(response)
        return prepared


    def POST(self):
        inbound = web.data()

        try:
            request = self.decode_inbound(inbound)
            response = self.process_request(request)
        except Exception as e:
            response = {
                'speech': "error: {}".format(e),
                'displayText': "error: {}".format(e)
            }

        outbound = self.prepare_response(response)

        self.dump_error(inbound, request, outbound)
        web.header("Content-Type", "application/json")
        return outbound
