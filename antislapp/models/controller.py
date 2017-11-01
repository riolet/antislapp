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

    def is_claim_complete(self, claim):
        """
        Check if a claim is completely examined. True if no more questions to ask.
        """
        complete = True
        if 'plead' not in claim or claim['plead'] == 'deny':
            complete = False
        for defence in Defence.DEFENCES:
            if defence not in claim:
                complete = False
                break
            if not claim[defence].get('complete', False):
                complete = False
                break
        return complete

    def next_defence_step(self, defence, defence_value):
        """
        Check if a defence is done being examined
        return None or a dict with keys:
            'step': either 'plead', the name of a defence, or 'question'
            'data': optional--only include when 'step' == 'question'
        """
        if defence_value is None:
            step = {
                'step': defence
            }
            return step

        if defence_value['complete'] is True:
            return None

        # do something special based on defence steps??
        if defence == 'Responsible Communication':
            step = {
                'step': 'question',
                'data': {'question': 'This is a special test follow-up question for responsible communication. Are you a human?'}
            }
            return step

        defence_value['complete'] = True
        return None

    def determine_next_step(self):
        """
        iterate through claims
        for each claim:
            if the claim has no plead:
                ask plead
            if the plead is deny:
                for each defence:
                    if the defence not fully examined:
                        ask defence
        """

        # determine which claim we should be looking at
        claims = self.defence.get_claims()
        claim_id = -1
        claim = None
        for i, clm in enumerate(claims):
            if not self.is_claim_complete(clm):
                claim_id = i
                claim = clm
                break

        if claim_id == -1:
            return None

        # have they pleaded for this claim?
        if 'plead' not in claim:
            next_step = {
                'claim_id': claim_id,
                'allegation': claim['allegation'],
                'next_step': 'plead'
            }
            return next_step

        # determine which defence we should be looking at
        next_defence_step = None
        for defence in Defence.DEFENCES:
            defence_value = claim.get(defence)
            next_defence_step = self.next_defence_step(defence, defence_value)
            if next_defence_step is not None:
                break

        assert next_defence_step is not None

        next_step = {
            'claim_id': claim_id,
            'allegation': claim['allegation'],
            'next_step': next_defence_step['step'],
            'data': next_defence_step['data'],
        }
        return next_step

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
        next_step = self.determine_next_step()
        # next_question has .acc_id, .acc, .qst OR is None
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
                'name': self.defence_triggers[next_step['next']],
                'data': next_step['data']
            }
        self.response.pop('speech', None)  # required to be absent
        self.response.pop('displayText', None)  # required to be absent

    def make_plea(self, context, params):
        cid = int(float(context['parameters']['acc_id']))
        # plead may be one of Defence.PLEADS ('agree', 'withhold', 'deny')
        self.defence.plead(cid, params['plead'])
        self.set_next_step()

    def defence_check(self, context, params):
        cid = int(float(context['parameters']['acc_id']))
        complete = False if context['parameters']['next_step'] == 'Responsible Communication' else True
        self.defence.add_defence(cid, context['parameters']['next_step'], params['valid'], complete)
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
            self.set_next_step()

    def

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
