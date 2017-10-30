import time
import traceback
import cPickle
import web
from antislapp import index

# data looks like:
# data:
#   sued = True/False
#   claims = [
#       {accusation: blah blah X
#       plead: agree/deny/withhold
#       Truth:
#           valid: true/false
#           facts: ['facts1', 'facts2']
#       Absolute Privilege:
#           valid: ...
#           facts: [...]
#       ...
#       },
#       {accusation: blah blah Y
#        ...
#       },
#       {accusation: blah blah Z
#       ...}


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

    @property
    def sued(self):
        return self.data['sued']

    @sued.setter
    def sued(self, sued):
        self.data['sued'] = bool(sued)

    @property
    def defendant(self):
        return self.data['defendant']

    @defendant.setter
    def defendant(self, name):
        if len(name) > 0:
            self.data['defendant'] = name

    @property
    def plaintiff(self):
        return self.data['plaintiff']

    @plaintiff.setter
    def plaintiff(self, name):
        if len(name) > 0:
            self.data['plaintiff'] = name

    def add_accusation(self, accusation, paragraph):
        self.data['claims'].append({
            'accusation': accusation,
            'paragraph': paragraph
        })

        return len(self.data['claims']) - 1

    def get_claims(self):
        return self.data.get('claims', [])

    def plead(self, accusation_id, plead):
        # Raises IndexError if accusation_id is missing.
        # Raises ValueError if plead isn't one of Defence.PLEADS.
        context = self.data['claims'][accusation_id]
        if plead not in Defence.PLEADS:
            raise ValueError("Plead must be one of {}".format(Defence.PLEADS))
        context['plead'] = plead

    def add_defence(self, accusation_id, defence, valid):
        # Raises IndexError if accusation_id is missing.
        # Raises ValueError if defence isn't one of Defence.DEFENCES
        # Casts valid to bool.
        context = self.data['claims'][accusation_id]
        if defence not in Defence.DEFENCES:
            raise ValueError("Defence must be one of {}".format(Defence.DEFENCES))
        context[defence] = {}
        context[defence]['valid'] = bool(valid)

    def add_fact(self, accusation_id, defence, facts):
        # Raises IndexError on missing accusation_id
        # Raises ValueError if defence has not been pleaded.
        context = self.data['claims'][accusation_id]
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

    def determine_next_question(self):
        for i, claim in enumerate(self.data['claims']):
            if 'plead' not in claim:
                question = {
                    'acc_id': i,
                    'acc': claim['accusation'],
                    'qst': 'plead'
                }
                return question
            elif claim['plead'] in ['withhold', 'agree']:
                continue
            else:
                for d in Defence.DEFENCES:
                    if d not in claim:
                        question = {
                            'acc_id': i,
                            'acc': claim['accusation'],
                            'qst': d
                        }
                        return question
        return None

    def report(self):
        if self.sued is None:
            sued = "may have "
        elif self.sued is True:
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
