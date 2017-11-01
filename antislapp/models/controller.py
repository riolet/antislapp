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
            'question': 'trigger-bool',
            'Truth': 'trigger-truth',
            'Absolute Privilege': 'trigger-absolute',
            'Qualified Privilege': 'trigger-qualified',
            'Fair Comment': 'trigger-fair',
            'Responsible Communication': 'trigger-responsible',
        }

    def set_sued(self, sued, plaintiff):
        self.defence.set_sued(sued)
        if plaintiff is not None:
            self.defence.set_plaintiff(plaintiff)

    def set_defendant(self, name):
        self.defence.set_defendant(name)

    def add_allegation(self, allegation, paragraph):
        return self.defence.add_allegation(allegation, paragraph)

    def get_definition(self, term):
        dfn = definitions.get(term.lower(), "That term isn't in the dictionary")
        self.response['speech'] = dfn
        self.response['displayText'] = dfn

    def set_next_step(self):
        next_step = self.defence.get_next_step()
        # next_question has .claim_id, .acc, .qst OR is None
        if next_step is None:
            self.response['followupEvent'] = {'name': 'trigger-summary', 'data': {}}
        else:
            params = {
                'claim_id': next_step['claim_id'],
                'allegation': next_step['allegation']
            }
            self.response['contextOut'] = [{
                'name': 'currentacc',
                'lifespan': 20,
                'parameters': params
            }]
            self.response['followupEvent'] = {
                'name': self.defence_triggers[next_step['next_step']],
                'data': next_step['data']
            }
        self.response.pop('speech', None)  # required to be absent
        self.response.pop('displayText', None)  # required to be absent

    def make_plea(self, context, params):
        cid = int(float(context['parameters']['claim_id']))
        # plead may be one of Defence.PLEADS ('agree', 'withhold', 'deny')
        self.defence.plead(cid, params['plead'])
        self.set_next_step()

    def defence_check(self, context, params):
        cid = int(float(context['parameters']['claim_id']))
        complete = False if context['parameters']['next_step'] == 'Responsible Communication' else True
        self.defence.add_defence(cid, context['parameters']['next_step'], params['applicable'])
        self.set_next_step()

    def done_facts(self, context):
        cid = int(float(context['parameters']['claim_id']))
        # TODO: this should break.
        self.defence.done_facts(cid, context['parameters']['defence'])
        self.set_next_step()

    def add_fact(self, context, fact):
        cid = int(float(context['parameters']['claim_id']))
        defence = context['parameters']['next_step']
        self.defence.add_fact(cid, defence, fact)
        self.response['contextOut'] = [{
            'name': 'currentacc',
            'lifespan': 20,
            'parameters': context['parameters']
        }]

    def boolean_answer(self, context, answer):
        cid = int(float(context['parameters']['claim_id']))
        defence = context['parameters']['defence']
        info = {
            'question': context['parameters']['question'],
            'answer': answer
        }
        self.defence.update_defence(cid, defence, info)
        self.set_next_step()

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
                if defence in claim and claim[defence].applicable:
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
