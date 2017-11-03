import copy
import time
import traceback
import cPickle
import web
from datetime import datetime
from antislapp import index

# data looks like:
# data:
#   sued = True/False
#   claims = [
#       {allegation: blah blah X
#       paragraph: "4"
#       plead: agree/deny/withhold
#       TruthDefence:
#           valid: true/false
#           facts: ['facts1', 'facts2']
#       AbsoluteDefence:
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
        self.applicable = data.get('applicable', None)
        self.facts_done = data.get('facts_done', False)
        self.facts = data.get('facts', [])

    def export_state(self):
        data = {
            'name': self.name,
            'applicable': self.applicable,
            'facts_done': self.facts_done,
            'facts': [str(fact) for fact in self.facts]
        }
        return data

    def next_step(self):
        next_step = None
        if self.applicable is None:
            next_step = {
                'next_step': self.name
            }
        elif self.applicable is True and self.facts_done is not True:
            next_step = {
                'next_step': 'facts',
            }
        return next_step

    def add_fact(self, fact):
        self.facts.append(fact)

    def update(self, params):
        pass


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
        self.extra_questions = [
            "There are a few questions to consider with the responsible communication defence. You don't need to answer yes to all of them, but should agree with more than not.\n\nDid your effort to research and verify your words match the seriousness of the allegation?",
            "Did your diligence also match the public importance of the matter? for example national security should be treated more seriously than everyday politics.",
            "Was the urgency to publish great enough that you couldn't afford a reasonable delay that would have detected the error?",
            "Did you consider the reliability of your sources? One must be more diligent if your sources are untrustworthy or biased.",
            "Did you try to get both sides of the story? It is important to try to be fair and will help your case.",
            "Was the defamatory statement's inclusion justifiable?",
            "Was the point that a defamatory statement had been made, rather than that it was fact? Like reporting on a heated exchange between politicians. This can be a defence if the statement can be attributed, you indicated it wasn't verified, both sides were fairly reported, and the context was clear."
        ]
        self.extra_answers = [None] * len(self.extra_questions)
        BaseDefence.__init__(self, 'Responsible Communication', state)

    def import_state(self, data):
        BaseDefence.import_state(self, data)
        self.extra_answers = data.get('extra_answers', [None] * len(self.extra_questions))

    def export_state(self):
        data = BaseDefence.export_state(self)
        data['extra_answers'] = self.extra_answers
        return data

    def next_step(self):
        next_step = None

        # if it hasn't been checked, check for applicability of this defence
        if self.applicable is None:
            next_step = {
                'next_step': self.name
            }

        # if this is applicable, ask any additional questions to verify.
        elif self.applicable is True and None in self.extra_answers:
            for i, ans in enumerate(self.extra_answers):
                if ans is None:
                    next_step = {
                        'next_step': 'question',
                        'data': {'question': self.extra_questions[i]}
                    }
                    return next_step

        # if this is applicable, and the special question was true, get the facts.
        elif self.applicable is True and None not in self.extra_answers and self.facts_done is not True:
            next_step = {
                'next_step': 'facts',
                'data': {}
            }
        return next_step

    def update(self, params):
        # params should include keys 'question' and 'answer'
        # 'answer' should be one of True, False, 'skip'

        # update the question list.
        question = params['question']
        answer = params['answer']
        index = self.extra_questions.index(question)
        self.extra_answers[index] = answer

        # if done, check if that changes anything.
        if None not in self.extra_answers:
            count_yes = self.extra_answers.count(True)
            count_no = self.extra_answers.count(False)
            if count_yes > 0 and count_yes > count_no:
                self.applicable = True
            else:
                self.applicable = False


def defence_ctor(state):
    return {
        'Truth': TruthDefence,
        'Absolute Privilege': AbsoluteDefence,
        'Qualified Privilege': QualifiedDefence,
        'Fair Comment': FairCommentDefence,
        'Responsible Communication': ResponsibleDefence
    }[state['name']](state)


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
        self.data = {}
        self.reset()
        self.load()

    def reset(self):
        self.data = {
            'sued': None,
            'defendant': None,
            'plaintiff': None,
            'claims': []
        }

    def load(self):
        qvars = {'cid': self.cid}
        rows = self.db.select(Defence.TABLE, what='data', where='conversation_id=$cid', vars=qvars)
        row = rows.first()
        if row is None:
            return

        try:
            data = cPickle.loads(str(row['data']))
            for claim in data['claims']:
                for Def_name, Def_state in claim.iteritems():
                    if Def_name in Defence.DEFENCES:
                        claim[Def_name] = defence_ctor(Def_state)

            now = int(time.time())
            self.db.update(Defence.TABLE, where='conversation_id=$cid', vars=qvars, atime=now)
            self.data = data
        except:
            traceback.print_exc()

    def save(self):
        data = copy.copy(self.data)
        claims = []
        for self_claim in self.data['claims']:
            claim = {}
            for k, v in self_claim.iteritems():
                if isinstance(v, BaseDefence):
                    claim[k] = v.export_state()
                else:
                    claim[k] = v
            claims.append(claim)
        data['claims'] = claims
        pickled_data = cPickle.dumps(data)
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

    def set_apology(self, happened, date, method):
        try:
            date = datetime.strptime(date, "%Y-%m-%d").strftime("%B %d, %Y")
        except:
            pass

        self.data['apology'] = {
            'applicable': happened,
            'date': date,
            'method': method
        }

    def set_defamatory(self, is_defamatory):
        self.data['is_defamatory'] = is_defamatory

    def set_damaging(self, is_damaging):
        self.data['is_damaging'] = is_damaging

    def add_allegation(self, allegation, paragraph):
        self.data['claims'].append({
            'allegation': allegation,
            'paragraph': paragraph,
            'plead': None
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

    def add_defence(self, claim_id, defence, applicable):
        # Raises IndexError if claim_id is missing.
        # Raises ValueError if defence isn't one of Defence.DEFENCES
        # Casts applicable to bool.
        context = self.data['claims'][claim_id]
        if defence not in Defence.DEFENCES:
            raise ValueError("Defence must be one of {}".format(Defence.DEFENCES))

        context[defence] = defence_ctor({'name': defence})
        context[defence].applicable = bool(applicable)

    def get_defence(self, claim_id, defence):
        context = self.data['claims'][claim_id]
        return context.get(defence, None)

    def update_defence(self, claim_id, defence, params):
        context = self.data['claims'][claim_id]
        defence_model = context[defence]
        defence_model.update(params)

    def add_fact(self, claim_id, defence, fact):
        # Raises IndexError on missing claim_id
        # Raises ValueError if defence has not been pleaded.
        context = self.data['claims'][claim_id]
        if defence not in context:
            raise ValueError
        context[defence].add_fact(fact)

    def done_facts(self, claim_id, defence):
        context = self.data['claims'][claim_id]
        if defence not in context:
            raise ValueError
        context[defence].facts_done = True

    def get_agreed(self):
        agreed = []
        for claim in self.data['claims']:
            if claim.get('plead', 'withhold') == 'agree':
                agreed.append(claim)
        return agreed

    def get_withheld(self):
        withheld = []
        for claim in self.data['claims']:
            print claim
            if claim['plead'] == 'withhold' or claim['plead'] is None:
                withheld.append(claim)
        return withheld

    def get_denied(self):
        denied = []
        for claim in self.data['claims']:
            if claim.get('plead', 'withhold') == 'deny':
                denied.append(claim)
        return denied

    def get_next_step(self):
        """
        possible next steps include:
            Get plead for claim X
            Process Truth...ResponsibleCommunication defence for claim X
        :return: None or dict with keys:
            claim_id: \d
            allegation: ""
            next_step: ""
            defence: ""  # optional
            data: {}  # optional
        """
        for claim_id, claim in enumerate(self.data['claims']):
            # Every claim needs to be pleaded one way or another.
            if claim['plead'] is None:
                next_step = {
                    'claim_id': claim_id,
                    'allegation': claim['allegation'],
                    'next_step': 'plead',
                }
                return next_step
            # Only claims that are denied have followup questions
            if claim['plead'] != 'deny':
                continue
            # Inquire about each possible defence.
            for defence in Defence.DEFENCES:
                d = claim.get(defence, None)

                # This defence hasn't been brought up yet.
                if d is None:
                    next_step = {
                        'claim_id': claim_id,
                        'allegation': claim['allegation'],
                        'next_step': defence,
                        'defence': defence,
                    }
                    return next_step

                # What to do if d isn't a BaseDefence instance?
                # if not isinstance(d, BaseDefence):
                #    del claim[defence]
                assert isinstance(d, BaseDefence)

                # If this defence is fully explored, move on.
                def_ns = d.next_step()
                if def_ns is None:
                    continue

                next_step = {
                    'claim_id': claim_id,
                    'allegation': claim['allegation'],
                    'next_step': def_ns['next_step'],
                    'defence': defence,
                    'data': def_ns.get('data', {}),
                }
                return next_step
        # done iterating over claims, now for general questions
        if 'is_defamatory' not in self.data:
            next_step = {'next_step': 'check-defamatory', 'claim_id': -1, 'allegation': ''}
            return next_step
        elif 'is_damaging' not in self.data:
            next_step = {'next_step': 'check-damaging', 'claim_id': -1, 'allegation': ''}
            return next_step
        elif 'apology' not in self.data:
            next_step = {'next_step': 'check-apology', 'claim_id': -1, 'allegation': ''}
            return next_step

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
