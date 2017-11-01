import time
import traceback
import cPickle
import web
from antislapp import index

# data looks like:
# data:
#   sued = True/False
#   claims = [
#       {allegation: blah blah X
#       plead: agree/deny/withhold
#       Truth:
#           valid: true/false
#           facts: ['facts1', 'facts2']
#       Absolute Privilege:
#           valid: ...
#           facts: [...]
#       ...
#       },
#       {allegation: blah blah Y
#        ...
#       },
#       {allegation: blah blah Z
#       ...}


class BaseDefence:
    def __init__(self, name, state):
        self.name = name
        self.applicable = None
        self.facts_done = False
        self.facts = []
        self.import_state(state)

    def import_state(self, data):
        self.applicable = data['applicable']
        self.facts_done = data['facts_done']
        self.facts = data['facts']

    def export_state(self):
        data = {
            'applicable': self.applicable,
            'facts_done': self.facts_done,
            'facts': [str(fact) for fact in self.facts]
        }
        return data

    def next_step(self):
        next_step = None
        if self.applicable is None:
            next_step = {
                'step': self.name
            }
        elif self.facts_done is not True:
            next_step = {
                'step': 'facts',
                'data': {'defence': self.name}
            }
        return next_step


class TruthDefence(BaseDefence):
    def __init__(self, state):
        BaseDefence.__init__(self, 'Truth', state)


class AbsoluteDefence(BaseDefence):
    def __init__(self, state):
        BaseDefence.__init__(self, 'Absolute Privilege', state)


class QualifiedDefence(BaseDefence):
    def __init__(self, state):
        BaseDefence.__init__(self, 'Qualified Privilege', state)


class FairCommentDefence(BaseDefence):
    def __init__(self, state):
        BaseDefence.__init__(self, 'Fair Comment', state)


class ResponsibleDefence(BaseDefence):
    def __init__(self, state):
        BaseDefence.__init__(self, 'Responsible Communication', state)
        self.special_question = None

    def import_state(self, data):
        BaseDefence.import_state(self, data)
        self.special_question = data['special']

    def export_state(self):
        data = BaseDefence.export_state(self)
        data['special'] = self.special_question
        return data

    def next_step(self):
        next_step = None
        if self.applicable is None:
            next_step = {
                'step': self.name
            }
        elif self.special_question is None:
            next_step = {
                'step': 'question',
                'data': {'question': 'This is a special test follow-up question for responsible communication. Are you a human?'}
            }
        elif self.facts_done is not True:
            next_step = {
                'step': 'facts',
                'data': {'defence': self.name}
            }
        return next_step


class Defence:
    TABLE = 'conversations'
    DEFENCES = ['Truth', 'Absolute Privilege', 'Qualified Privilege', 'Fair Comment', 'Responsible Communication']
    PLEADS = ['agree', 'deny', 'withhold']

    def __init__(self, db, conversation_id):
        """
        :type db: web.DB
        :type conversation_id: basestring
        """
        self.db = db
        self.cid = conversation_id
        qvars = {
            'cid': conversation_id
        }
        rows = self.db.select(Defence.TABLE, what='data', where='conversation_id=$cid', vars=qvars)
        row = rows.first()
        if row is None:
            self.reset()
        else:
            try:
                self.data = cPickle.loads(str(row['data']))
                now = int(time.time())
                self.db.update(Defence.TABLE, where='conversation_id=$cid', vars=qvars, atime=now)
            except:
                traceback.print_exc()
                self.reset()

    def reset(self):
        self.data = {
            'sued': None,
            'defendant': None,
            'plaintiff': None,
            'claims': []
        }

    def save(self):
        pickled_data = cPickle.dumps(self.data)
        now = int(time.time())
        with self.db.transaction():
            self.db.delete(Defence.TABLE, where='conversation_id=$cid', vars={'cid': self.cid})
            self.db.insert(Defence.TABLE, conversation_id=self.cid, data=pickled_data, atime=now)

    def get_sued(self):
        return self.data['sued']

    def set_sued(self, sued):
        self.data['sued'] = bool(sued)

    def get_defendant(self):
        return self.data['defendant']

    def set_defendant(self, name):
        if len(name) > 0:
            self.data['defendant'] = name

    def get_plaintiff(self):
        return self.data['plaintiff']

    def set_plaintiff(self, name):
        if len(name) > 0:
            self.data['plaintiff'] = name

    def add_allegation(self, allegation, paragraph):
        self.data['claims'].append({
            'allegation': allegation,
            'paragraph': paragraph
        })

        return len(self.data['claims']) - 1

    def get_claims(self):
        return self.data.get('claims', [])

    def plead(self, claim_id, plead):
        # Raises IndexError if claim_id is missing.
        # Raises ValueError if plead isn't one of Defence.PLEADS.
        context = self.data['claims'][claim_id]
        if plead not in Defence.PLEADS:
            raise ValueError("Plead must be one of {}".format(Defence.PLEADS))
        context['plead'] = plead

    def add_defence(self, claim_id, defence, valid, complete):
        # Raises IndexError if claim_id is missing.
        # Raises ValueError if defence isn't one of Defence.DEFENCES
        # Casts valid to bool.
        context = self.data['claims'][claim_id]
        if defence not in Defence.DEFENCES:
            raise ValueError("Defence must be one of {}".format(Defence.DEFENCES))
        context[defence] = {}
        context[defence]['valid'] = bool(valid)
        context[defence]['complete'] = complete

    def get_defence(self, claim_id, defence):
        context = self.data['claims'][claim_id]
        return context.get(defence, None)

    def update_defence(self, claim_id, defence, key, value):
        context = self.data['claims'][claim_id]
        defence = context[defence]
        defence[key] = value

    def add_fact(self, claim_id, defence, facts):
        # Raises IndexError on missing claim_id
        # Raises ValueError if defence has not been pleaded.
        context = self.data['claims'][claim_id]
        if defence not in context:
            raise ValueError
        if 'facts' in context[defence]:
            context[defence]['facts'].append(facts)
        else:
            context[defence]['facts'] = [facts]

    def get_agreed(self):
        agreed = []
        for claim in self.data['claims']:
            if claim.get('plead', 'withhold') == 'agree':
                agreed.append(claim)
        return agreed

    def get_withheld(self):
        withheld = []
        for claim in self.data['claims']:
            if claim.get('plead', 'withhold') == 'withhold':
                withheld.append(claim)
        return withheld

    def get_denied(self):
        denied = []
        for claim in self.data['claims']:
            if claim.get('plead', 'withhold') == 'deny':
                denied.append(claim)
        return denied

    def report(self):
        if self.get_sued() is None:
            sued = "may have "
        elif self.get_sued() is True:
            sued = "have "
        else:
            sued = "have not "
        agrees = index.join_list([claim['paragraph'] for claim in self.get_agreed()])
        withholds = index.join_list([claim['paragraph'] for claim in self.get_withheld()])
        denies = index.join_list([claim['paragraph'] for claim in self.get_denied()])
        p_agree = "You agree with the claims in paragraphs {}. ".format(agrees)
        p_withhold = "You cannot respond to claims in paragraphs {}. ".format(withholds)
        p_deny = "You deny the allegations in paragraphs {}. ".format(denies)

        summary = "In summary, you {sued}been sued. ".format(sued=sued)
        if agrees:
            summary += p_agree
        if denies:
            summary += p_deny
        if withholds:
            summary += p_withhold
        return summary.strip()
