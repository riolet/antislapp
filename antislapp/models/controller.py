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
                'name': self.defence_triggers[next['def']],
                'data': {}
            }
        del self.response['speech']  # required to be absent
        del self.response['displayText']  # required to be absent

    def make_plea(self, context, params):
        self.defence.plead(context['acc_id'], params['plead'])
        self.done_accusations()

    def defence_check(self, context, params):
        self.defence.add_defence(context['acc_id'], context['qst'], params['valid'])
        self.done_accusations()

    def report(self):
        report = self.defence.report()
        form = Form18A(self.cid)

        form.set_unanswered(self.defence.get_undefended())
        form.set_denials(self.defence.get_defended())

        evidence = []
        accusations = self.defence.get_accusations()
        defences = self.defence.get_defences()
        for i, acc in enumerate(accusations):
            ds = [k for k, v in defences.get(i, {}).iteritems() if v is not False]
            if len(ds) > 1:
                p = 'The defendant denies "{}" with a defence of {}'.format(acc, self.join_list(ds))
            else:
                p = 'The defendant denies "{}" with a defence of {}'.format(acc, ds[0])
            evidence.append(p)
        form.set_evidence(evidence)
        form.write()

        report = report + " Download statement of defence here: http://riobot.centralus.cloudapp.azure.com{}".format(form.get_link())

        self.defence.get_accusations()
        self.response['speech'] = report
        self.response['displayText'] = report

    def reset(self):
        self.defence.reset()

    def save(self):
        self.defence.save()

    def get_response(self):
        return self.response