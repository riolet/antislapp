from antislapp import index
from antislapp.models.defence import Defence
from antislapp.models.formS2600 import FormS2600
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
            'facts': 'trigger-facts',
            'Truth': 'trigger-truth',
            'Absolute Privilege': 'trigger-absolute',
            'Qualified Privilege': 'trigger-qualified',
            'Fair Comment': 'trigger-fair',
            'Responsible Communication': 'trigger-responsible',
            'check-defamatory': 'trigger-defamatory',
            'check-damaging': 'trigger-damaging',
            'check-apology': 'trigger-apology',
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
            data = next_step.pop('data', {})
            step = next_step.pop('next_step', 'report')
            self.response['contextOut'] = [{
                'name': 'currentacc',
                'lifespan': 20,
                'parameters': next_step
            }]
            self.response['followupEvent'] = {
                'name': self.defence_triggers[step],
                'data': data
            }
        self.response.pop('speech', None)  # required to be absent
        self.response.pop('displayText', None)  # required to be absent

    def make_plea(self, context, params):
        cid = int(float(context['parameters']['claim_id']))
        # plead may be one of Defence.PLEADS ('agree', 'withhold', 'deny')
        self.defence.plead(cid, params['plead'])
        self.set_next_step()

    def defence_check(self, context, params):
        defence = context['parameters']['defence']
        self.defence.add_defence(defence, params['applicable'])
        self.set_next_step()

    def add_fact(self, context, fact):
        defence = context['parameters']['defence']
        self.defence.add_fact(defence, fact)

    def done_facts(self, context):
        defence = context['parameters']['defence']
        self.defence.done_facts(defence)
        self.set_next_step()

    def set_damaging(self, damaging):
        self.defence.set_damaging(damaging)
        self.set_next_step()

    def set_defamatory(self, defamatory):
        self.defence.set_defamatory(defamatory)
        self.set_next_step()

    def set_apology(self, params):
        self.defence.set_apology(params['happened'], params['date'], params['method'])
        self.set_next_step()

    def boolean_answer(self, context, answer):
        defence = context['parameters']['defence']
        info = {
            'question': context['parameters']['question'],
            'answer': answer
        }
        self.defence.update_defence(defence, info)
        self.set_next_step()

    def report(self):
        report = self.defence.report()
        form = FormS2600(self.cid)

        if self.defence.get_defendant() is not None:
            form.defendant = self.defence.get_defendant()
        if self.defence.get_plaintiff() is not None:
            form.plaintiff = self.defence.get_plaintiff()
        form.claims_unanswered = self.defence.get_withheld()
        form.claims_denied = self.defence.get_denied()
        form.claims_admitted = self.defence.get_agreed()
        if 'apology' in self.defence.data and self.defence.data['apology']['applicable'] is True:
            form.apology_given = True
            form.apology_date = self.defence.data['apology']['date']
            form.apology_method = self.defence.data['apology']['method']
        form.was_damaging = self.defence.data.get('is_damaging', None)
        form.was_defamatory = self.defence.data.get('is_defamatory', None)

        defences = self.defence.get_defences()
        defence_paragraphs = [d.report() for d in defences.values() if d.applicable]
        form.set_defences(defence_paragraphs)

        fact_paragraphs = []
        form.set_additional_facts(fact_paragraphs)

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
