from antislapp import index
from antislapp.models.defence import Defence
from antislapp.models.form18a import Form18A


class Controller:
    def __init__(self, conversation_id, default_response):
        self.cid = conversation_id
        self.default = default_response
        self.defence = Defence(index.db, self.cid)
        self.response = {
            'speech': default_response,
            'displayText': default_response,
            #'event': {"name":"<event_name>","data":{"<parameter_name>":"<parameter_value>"}},
            #'data': _,
            #'contextOut': [{"name":"weather", "lifespan":2, "parameters":{"city":"Rome"}}],
            # context name must be lowercase
            'source': 'riobot',
        }
        self.defence_triggers = {
            'plead': 'trigger-plead',
            'Truth': 'trigger-truth',
            'Absolute Privilege': 'trigger-absolute',
            'Qualified Privilege': 'trigger-qualified',
            'Fair Comment': 'trigger-fair',
            'Responsible Communication': 'trigger-responsible'
        }

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

    def set_sued(self, sued):
        self.defence.set_sued(sued)

    def add_accusation(self, accusation):
        self.defence.add_accusation(accusation)

    def done_accusations(self):
        next = self.defence.determine_next_question()
        # next has .acc_id, .acc, .def OR is None
        if next is None:
            self.response['followupEvent'] = {'name': 'trigger-summary', 'data': {}}
        else:
            self.response['contextOut'] = [{
                'name': 'currentacc',
                'lifespan': 2,
                'parameters': next
            }]
            self.response['followupEvent'] = {
                'name': self.defence_triggers[next['qst']],
                'data': {}
            }
        del self.response['speech']  # required to be absent
        del self.response['displayText']  # required to be absent

    def make_plea(self, context, params):
        cid = int(float(context['acc_id']))
        self.defence.plead(cid, params['plead'])
        self.done_accusations()

    def defence_check(self, context, params):
        cid = int(float(context['acc_id']))
        self.defence.add_defence(cid, context['qst'], params['valid'])
        self.done_accusations()

    def report(self):
        report = self.defence.report()
        form = Form18A(self.cid)

        form.set_unanswered([claim['accusation'] for claim in self.defence.get_withheld()])
        form.set_denials([claim['accusation'] for claim in self.defence.get_denied()])
        form.set_admissions([claim['accusation'] for claim in self.defence.get_agreed()])

        evidence = []
        claims = self.defence.get_claims()
        for i, claim in enumerate(claims):
            if claim['plead'] != 'deny':
                continue

            for d in Defence.DEFENCES:
                if d in claim and claim[d]['valid']:
                    e = claim[d]['evidence']
                    if len(e) > 1:
                        p = 'The defendant denies "{}" with a defence of {}'.format(claim['accusation'],
                                                                                    self.join_list(e))
                        evidence.append(p)
                    elif len(e) == 1:
                        p = 'The defendant denies "{}" with a defence of {}'.format(claim['accusation'], e[0])
                        evidence.append(p)
        form.set_evidence(evidence)
        form.write()

        report = report + " Download statement of defence here: http://riobot.centralus.cloudapp.azure.com{}".format(form.get_link())

        self.response['speech'] = report
        self.response['displayText'] = report

    def reset(self):
        self.defence.reset()

    def save(self):
        self.defence.save()

    def get_response(self):
        return self.response