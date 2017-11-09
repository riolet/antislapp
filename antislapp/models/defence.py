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
#       ...
#       },
#       {allegation: blah blah Y
#        ...
#       },
#       {allegation: blah blah Z
#       ...}
#   defences = {
#       TruthDefence:
#           valid: true/false
#           facts: ['facts1', 'facts2']
#           extra_questions/answers: [...]
#       AbsoluteDefence:
#           valid: ...
#           facts: [...]
#           extra_questions/answers: [...]
#       ...
#   }


class BaseDefence:
    def __init__(self, name, state):
        self.name = name
        self.applicable = None
        self.facts_done = False
        self.facts = []
        self.extra_questions = []
        self.extra_answers = [None] * len(self.extra_questions)
        self.import_state(state)

    def import_state(self, data):
        self.applicable = data.get('applicable', None)
        self.facts_done = data.get('facts_done', False)
        self.facts = data.get('facts', [])
        self.extra_answers = data.get('extra_answers', [None] * len(self.extra_questions))

    def export_state(self):
        data = {
            'name': self.name,
            'applicable': self.applicable,
            'facts_done': self.facts_done,
            'facts': [str(fact) for fact in self.facts],
            'extra_answers': self.extra_answers,
        }
        return data

    def next_step(self):
        next_step = None
        # Ask if this defence might apply
        if self.applicable is None:
            next_step = {
                'next_step': self.name
            }

        # Ask any extra questions relevant to this defence
        elif self.applicable is True and None in self.extra_answers:
            for i, ans in enumerate(self.extra_answers):
                if ans is None:
                    next_step = {
                        'next_step': 'question',
                        'data': {'question': self.extra_questions[i]}
                    }
                    return next_step

        # Collect any additional relevant facts
        elif self.applicable is True and self.facts_done is not True:
            next_step = {
                'next_step': 'facts',
            }
        return next_step

    def add_fact(self, fact):
        self.facts.append(fact)

    def determine_eligibility(self):
        # only update 'applicable' if all extra_questions have been answered
        if None in self.extra_answers:
            return

        count_yes = self.extra_answers.count(True)
        count_no = self.extra_answers.count(False)
        self.applicable = count_yes > 0 and count_yes > count_no

    def submit_extra_answer(self, question, answer):
        # params should include keys 'question' and 'answer'
        # 'answer' should be one of True, False, 'skip'

        # update the question list.
        q_index = self.extra_questions.index(question)
        self.extra_answers[q_index] = answer

        # if done, check if that changes anything.
        self.determine_eligibility()

    def update(self, params):
        if 'question' in params and 'answer' in params:
            self.submit_extra_answer(params['question'], params['answer'])

    def report(self):
        raise NotImplementedError


class TruthDefence(BaseDefence):
    def __init__(self, state):
        BaseDefence.__init__(self, 'Truth', state)
        self.extra_questions = [
            'So everything you stated was fact, or can be proven by facts?',
            'Were your statements based on information from reliable sources?',
            'Do you have evidence or witnesses you can use to prove this claim?',
        ]
        if len(self.extra_answers) != len(self.extra_questions):
            self.extra_answers = [None] * len(self.extra_questions)

    def determine_eligibility(self):
        if None in self.extra_answers:
            return

        # if Q1 is True and at least one of Q2/Q3 are true.
        count_yes = self.extra_answers.count(True)
        self.applicable = count_yes >= 2 and self.extra_answers[0] is True

    def report(self):
        report = ""
        if self.extra_answers[0] is True:
            report += "the defendant's statements was a statement of provable fact, and "
        if self.extra_answers[1] is True:
            report += "the facts used were based upon reliable sources, thus "
        report += "any statements about the plaintiff were fully protected by the defence of truth or justification."
        return report


class AbsoluteDefence(BaseDefence):
    def __init__(self, state):
        BaseDefence.__init__(self, 'Absolute Privilege', state)
        self.extra_questions = [
            'Were you participating in a judicial proceeding or speaking before a legislative assemble when you made your statements? In other words, were you in court?',
            'Were you asked to make a statement or testify?',
            'Did you make these statements to a reporter or someone not involved in the case?'
        ]
        if len(self.extra_answers) != len(self.extra_questions):
            self.extra_answers = [None] * len(self.extra_questions)

    def determine_eligibility(self):
        if None in self.extra_answers:
            return

        # if Q1 is True and at least one of Q2/Q3 are true.
        count_yes = 0
        count_no = 0
        if self.extra_answers[1] is True:
            count_yes += 1
        elif self.extra_answers[1] is False:
            count_no += 1
        if self.extra_answers[2] is False:
            count_yes += 1
        elif self.extra_answers[2] is True:
            count_no += 1

        self.applicable = self.extra_answers[0] is True and count_yes > 0

    def report(self):
        return "any statements about the plaintiff were fully protected by the defence of absolute privilege."


class QualifiedDefence(BaseDefence):
    def __init__(self, state):
        BaseDefence.__init__(self, 'Qualified Privilege', state)
        self.extra_questions = [
            'Did you have a duty--legal, social, or moral--to make the statement(s) in question? e.g. answering police inquiries or communication between traders and credit agencies.',
            'Did you make your statements without malice? e.g. Did you honestly believe in the truth of your statement?',
            'Did you only make your statement to the people who needed to hear it?',
        ]
        if len(self.extra_answers) != len(self.extra_questions):
            self.extra_answers = [None] * len(self.extra_questions)

    def report(self):
        if self.extra_answers[0] and self.extra_answers[1]:
            report = "the defendant was bound by legal, social, or moral duty to make their statement, and any statements made by the defendant were made without malice and are fully protected by the defence of qualified privilege."
        elif self.extra_answers[0]:
            report = "the defendant was bound by legal, social, or moral duty to make their statement, and any statements about the plaintiff were fully protected by the defence of qualified privilege."
        else:
            report = "any statements about the plaintiff were fully protected by the defence of qualified privilege."
        return report


class FairCommentDefence(BaseDefence):
    def __init__(self, state):
        BaseDefence.__init__(self, 'Fair Comment', state)
        self.extra_questions = [
            'Were your words a comment/observation/opinion and would someone recognize your words as such?',
            'Were your statements based on facts that were true, and was this basis apparent to your audience?',
            'Could any person honestly express that opinion you made based on the facts?',
            'Was the subject matter of your opinion of "public interest"?',
        ]
        if len(self.extra_answers) != len(self.extra_questions):
            self.extra_answers = [None] * len(self.extra_questions)

    def determine_eligibility(self):
        if None in self.extra_answers:
            return

        # if Q1 is True and at least one of Q2/Q3 are true.
        count_yes = self.extra_answers.count(True) - 1
        count_no = self.extra_answers.count(False)

        self.applicable = self.extra_answers[0] is True and count_yes > count_no

    def report(self):
        return "any statements about the plaintiff were the defendant's opinion based solely on published facts, and are protected by the defence of fair comment"


class ResponsibleDefence(BaseDefence):
    def __init__(self, state):
        BaseDefence.__init__(self, 'Responsible Communication', state)
        self.extra_questions = [
            "Did your effort to research and verify your words match the seriousness of the allegation?",
            "Did your diligence also match the public importance of the matter? for example national security should be treated more seriously than everyday politics.",
            "Was the urgency to publish great enough that you couldn't afford a reasonable delay that would have detected the error?",
            "Did you consider the reliability of your sources? One must be more diligent if your sources are untrustworthy or biased.",
            "Did you try to get both sides of the story? It is important to try to be fair and will help your case.",
            "Was the defamatory statement's inclusion justifiable?",
            "Was the point that a defamatory statement had been made, rather than that it was fact? Like reporting on a heated exchange between politicians. This can be a defence if the statement can be attributed, you indicated it wasn't verified, both sides were fairly reported, and the context was clear."
        ]
        if len(self.extra_answers) != len(self.extra_questions):
            self.extra_answers = [None] * len(self.extra_questions)

    def report(self):
        return "the defendant's statements were made without malice on a matter of public interest on the basis of information from apparently reliable and qualified sources, and were protected by the defence of responsible communication."


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
            'courtName': None,
            'claims': [],
            'defences': {},
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

    def get_court_name(self):
        return self.data['courtName']

    def set_court_name(self, court_name):
        self.data['courtName'] = court_name

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

    def add_defence(self, defence, applicable):
        # Raises ValueError if defence isn't one of Defence.DEFENCES
        # Casts applicable to bool.
        defences = self.data['defences']
        if defence not in Defence.DEFENCES:
            raise ValueError("Defence must be one of {}".format(Defence.DEFENCES))

        defences[defence] = defence_ctor({'name': defence})
        defences[defence].applicable = bool(applicable)

    def get_defences(self):
        return self.data.get('defences', {})

    def update_defence(self, defence, params):
        defence_model = self.data['defences'][defence]
        defence_model.update(params)

    def add_fact(self, defence, fact):
        # Raises IndexError on missing defence
        defence_model = self.data['defences'][defence]
        defence_model.add_fact(fact)

    def done_facts(self, defence):
        # Raises IndexError on missing defence
        defence_model = self.data['defences'][defence]
        defence_model.facts_done = True

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
        # plead all claims first.
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
        denied_paragraphs_list = [str(claim['paragraph']) for claim in self.get_denied()]
        if len(denied_paragraphs_list) == 0:
            next_step = {
                'next_step': "exit-deny",
            }
            return next_step

        denied_paragraphs = index.join_list(denied_paragraphs_list)
        prev_d_model = None
        prev_quote = " "
        d_model = None
        for defence in Defence.DEFENCES:
            defences = self.get_defences()
            d_model = defences.get(defence, None)

            if prev_d_model and prev_d_model.applicable is True:
                prev_quote = "Great, I've attached the {} defence to your statement.".format(prev_d_model.name)
            elif prev_d_model:
                prev_quote = "I've left out the {} defence.".format(prev_d_model.name)

            # This defence hasn't been brought up yet.
            if d_model is None:
                next_step = {
                    'paragraphs': denied_paragraphs,
                    'next_step': defence,
                    'defence': defence,
                    'data': {'preface': prev_quote}
                }
                return next_step

            # What to do if d isn't a BaseDefence instance?
            # if not isinstance(d, BaseDefence):
            #    del claim[defence]
            assert isinstance(d_model, BaseDefence)

            # If this defence is fully explored, move on.
            def_ns = d_model.next_step()
            if def_ns is None:
                prev_d_model = d_model
                continue

            data = def_ns.get('data', {})
            data['preface'] = prev_quote

            next_step = {
                'paragraphs': denied_paragraphs,
                'next_step': def_ns['next_step'],
                'defence': defence,
                'data': data,
            }
            return next_step
        if d_model and d_model.applicable is True:
            prev_quote = "Great, I've attached the {} defence to your statement.".format(prev_d_model.name)
        elif d_model:
            prev_quote = "I've left out the {} defence.".format(prev_d_model.name)

        # done iterating over claims and defences, now for general questions
        if 'is_defamatory' not in self.data:
            next_step = {'next_step': 'check-defamatory',
                         'data': {'preface': prev_quote}}
            return next_step
        elif 'is_damaging' not in self.data:
            next_step = {'next_step': 'check-damaging'}
            return next_step
        elif 'apology' not in self.data:
            next_step = {'next_step': 'check-apology'}
            return next_step
        elif self.data['courtName'] is None:
            next_step = {'next_step': 'check-court'}
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
