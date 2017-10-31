import re
from antislapp import index
from antislapp.models.defence import Defence
from antislapp.models.form18a import Form18A
from antislapp.models.suitsteps import SuitSteps
from antislapp.models.definitions import definitions


class Controller:
    def __init__(self, conversation_id, default_response):
        self.cid = conversation_id
        self.domain = "https://riobot.centralus.cloudapp.azure.com"
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

    def set_sued(self, sued):
        self.defence.set_sued(sued)

    def set_defendant(self, name):
        self.defence.set_defendant(name)

    def set_plaintiff(self, name):
        self.defence.set_plaintiff(name)
        self.done_accusations()

    def add_accusation(self, accusation, paragraph):
        return self.defence.add_accusation(accusation, paragraph)

    def get_definition(self, term):
        dfn = definitions.get(term.lower(), "That term isn't in the dictionary")
        self.response['speech'] = dfn
        self.response['displayText'] = dfn

    def done_accusations(self):
        next_question = self.defence.determine_next_question()
        # next_question has .acc_id, .acc, .qst OR is None
        if next_question is None:
            if self.defence.get_plaintiff() is None:
                self.response['followupEvent'] = {'name': 'trigger-plaintiff', 'data': {}}
            else:
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

        if self.defence.get_defendant() is not None:
            form.set_defendant(self.defence.get_defendant())
        if self.defence.get_plaintiff() is not None:
            form.set_plaintiff(self.defence.get_plaintiff())
        form.set_unanswered(self.defence.get_withheld())
        form.set_denials(self.defence.get_denied())
        form.set_admissions(self.defence.get_agreed())

        fact_paragraphs = []
        claims = self.defence.get_claims()
        for i, claim in enumerate(claims):
            if claim['plead'] != 'deny':
                continue

            for defence in Defence.DEFENCES:
                if defence in claim and claim[defence]['valid']:
                    facts = claim[defence].get('facts', [])
                    for fact in facts:
                        p_number = claim['paragraph']
                        fact = re.sub(r'\bme\b', 'the defendant', fact)
                        fact = re.sub(r"\b[Ii]('m|\sam)\b", 'the defendant is', fact)
                        fact = re.sub(r'\b[Ii]\b', 'the defendant', fact)
                        p = 'With respect to allegations in paragraph {}, the defendant claims {}'.format(p_number, fact)
                        fact_paragraphs.append(p)
        form.set_facts(fact_paragraphs)
        form.write()

        report = report + "\n\nDownload your Statement of Defence " \
                          "[{}{}](here).".format(self.domain, form.get_link())

        # steps
        steps = SuitSteps(self.cid)
        steps.populate(self.defence)
        steps.write()
        report = report + "\n\nDownload your Defence Guide " \
                          "[{}{}](here).".format(self.domain, steps.get_link())

        self.response['speech'] = report
        self.response['displayText'] = report

    def reset(self):
        self.defence.reset()

    def save(self):
        self.defence.save()

    def get_response(self):
        return self.response
