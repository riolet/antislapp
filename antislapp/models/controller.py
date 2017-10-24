from antislapp import index
from antislapp.models.defence import Defence
from antislapp.models.form18a import Form18A
from antislapp.models.definitions import definitions


class Controller:
    def __init__(self, conversation_id, default_response):
        self.cid = conversation_id
        self.default = default_response
        self.defence = Defence(index.db, self.cid)
        self.response = {
            'speech': default_response,
            'displayText': default_response,
            # 'event': {"name":"<event_name>","data":{"<parameter_name>":"<parameter_value>"}},
            # 'data': _,
            # 'contextOut': [{"name":"weather", "lifespan":2, "parameters":{"city":"Rome"}}],
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
        count = len(items)
        if count == 0:
            joined = ''
        elif count == 1:
            joined = items[0]
        elif count == 2:
            joined = "{} and {}".format(*items)
        else:
            joined = "{}, and {}".format(", ".join(items[:-1]), items[-1])
        return joined

    def set_sued(self, sued):
        self.defence.set_sued(sued)

    def add_accusation(self, accusation):
        return self.defence.add_accusation(accusation)

    def get_definition(self, term):
        dfn = definitions.get(term.lower(), "That term isn't in the dictionary")
        self.response['speech'] = dfn
        self.response['displayText'] = dfn

    def done_accusations(self):
        next_question = self.defence.determine_next_question()
        # next_question has .acc_id, .acc, .qst OR is None
        if next_question is None:
            self.response['followupEvent'] = {'name': 'trigger-summary', 'data': {}}
        else:
            self.response['contextOut'] = [{
                'name': 'currentacc',
                'lifespan': 20,
                'parameters': next_question
            }]
            self.response['followupEvent'] = {
                'name': self.defence_triggers[next_question['qst']],
                'data': {}
            }
        self.response.pop('speech', None)  # required to be absent
        self.response.pop('displayText', None)  # required to be absent

    def make_plea(self, context, params):
        cid = int(float(context['parameters']['acc_id']))
        # plead may be one of Defence.PLEADS ('agree', 'withhold', 'deny')
        self.defence.plead(cid, params['plead'])
        self.done_accusations()

    def defence_check(self, context, params):
        cid = int(float(context['parameters']['acc_id']))
        self.defence.add_defence(cid, context['parameters']['qst'], params['valid'])
        if params['valid']:
            self.response['contextOut'] = [{
                'name': 'currentacc',
                'lifespan': 20,
                'parameters': context['parameters']
            }]
            self.response['followupEvent'] = {
                'name': 'trigger-facts',
                'data': {}
            }
            self.response.pop('speech', None)  # required to be absent
            self.response.pop('displayText', None)  # required to be absent
        else:
            self.done_accusations()

    def add_fact(self, context, fact):
        cid = int(float(context['parameters']['acc_id']))
        defence = context['parameters']['qst']
        self.defence.add_fact(cid, defence, fact)
        self.response['contextOut'] = [{
            'name': 'currentacc',
            'lifespan': 20,
            'parameters': context['parameters']
        }]

    def report(self):
        report = self.defence.report()
        form = Form18A(self.cid)

        form.set_unanswered([claim['accusation'] for claim in self.defence.get_withheld()])
        form.set_denials([claim['accusation'] for claim in self.defence.get_denied()])
        form.set_admissions([claim['accusation'] for claim in self.defence.get_agreed()])

        fact_paragraphs = []
        claims = self.defence.get_claims()
        for i, claim in enumerate(claims):
            if claim['plead'] != 'deny':
                continue

            for defence in Defence.DEFENCES:
                if defence in claim and claim[defence]['valid']:
                    facts = claim[defence].get('facts', [])
                    for fact in facts:
                        allegation = claim['accusation']
                        fact = fact.replace('me', 'the defendant')
                        fact = fact.replace('I', 'the defendant')
                        p = 'With respect to allegations of "{}", the defendant claims {}'.format(allegation, fact)
                        fact_paragraphs.append(p)
        form.set_facts(fact_paragraphs)
        form.write()

        report = report + " Download your statement of defence here: " \
                          "http://riobot.centralus.cloudapp.azure.com{}".format(form.get_link())

        self.response['speech'] = report
        self.response['displayText'] = report

    def reset(self):
        self.defence.reset()

    def save(self):
        self.defence.save()

    def get_response(self):
        return self.response
