import re
from antislapp import index
from antislapp.models.defence import Defence
from antislapp.models.formS2600 import FormS2600
from antislapp.models.suitsteps import SuitSteps
from antislapp.models.definitions import definitions


class Controller:
    def __init__(self, conversation_id, default_response):
        self.cid = conversation_id
        # self.domain = "https://riobot.centralus.cloudapp.azure.com"
        self.domain = "https://antislapp.ca"
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
            'check-antislapp': 'trigger-antislapp',
            'check-defamatory': 'trigger-defamatory',
            'check-damaging': 'trigger-damaging',
            'check-apology': 'trigger-apology',
            'check-court': 'trigger-court',
            'exit-deny': 'trigger-exit-deny',
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
            self.response['followupEvent'] = {'name': 'trigger-summary', 'data': {'preface': ' '}}
        else:
            data = next_step.pop('data', {})
            if 'preface' not in data:
                data['preface'] = ' '
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

    def set_antislapp(self, ontario, public):
        self.defence.set_antislapp(ontario and public)
        self.set_next_step()

    def set_court_name(self, court_name):
        self.defence.set_court_name(court_name)
        self.set_next_step()

    def boolean_answer(self, context, answer):
        defence = context['parameters']['defence']
        info = {
            'question': context['parameters']['question'],
            'answer': answer
        }
        self.defence.update_defence(defence, info)
        self.set_next_step()

    def get_missing_numbers(self, found_numbers):
        numbers = []
        for fnum in found_numbers:
            if type(fnum) in (float, int):
                numbers.append(int(fnum))
                continue

            numstrings = fnum.split(",")
            for numstring in numstrings:
                if numstring.strip().isdigit():
                    numbers.append(int(numstring))
                    continue
                # ranges of form 1..3 or 1-3 with spaces anywhere
                match = re.match(r'\s*(\d+)\s*(?:-+|\.\.+)\s*(\d+)\s*', numstring)
                if match:
                    a = int(match.group(1))
                    b = int(match.group(2))
                    numbers.extend(range(min(a, b), max(a, b) + 1))

        highest = max(numbers)
        missing = []
        for i in range(1, highest):
            if i not in numbers:
                missing.append(i)
        groups = self.group_ranges(missing)
        return groups

    def group_ranges(self, numbers):
        # turns lists like [3,2,7,6,8] and [1,2,3,4,6,7,9,10]
        # into lists like ['2-3', '6-8'] and ['1-4', '6-7', '9-10']
        if len(numbers) == 0:
            return []

        nums = sorted(list(set(numbers)))

        grouped_missing = []
        prev = nums[0]
        run = 0
        for n in nums[1:]:
            if n == prev + 1:
                run += 1
            else:
                if run == 0:
                    grouped_missing.append("{}".format(prev))
                else:
                    grouped_missing.append("{}-{}".format(prev - run, prev))
                run = 0
            prev = n
        if run == 0:
            grouped_missing.append("{}".format(prev))
        else:
            grouped_missing.append("{}-{}".format(prev - run, prev))
        return grouped_missing

    def report(self):
        report = self.defence.report()

        # if any paragraphs are missing from the pleadings, mention them here
        missing_paragraphs = self.get_missing_numbers([claim['paragraph'] for claim in self.defence.get_claims()])
        if missing_paragraphs:
            report += "\n\nSome paragraph numbers ({}) of allegations made seem to be missing. It is important that " \
                      "all allegation paragraphs are accounted for in paragraphs 1, 2, or 3 of Part 1 Division 1 in " \
                      "your defence below.".format(index.join_list(missing_paragraphs))

        # If antislapp legislation applies, mention that!
        if self.defence.get_antislapp() is True:
            report += "\n\nSince you're being sued in Ontario, and it's about a matter of public interest, you can " \
                      "request the court dismiss the proceeding in accordance with the Protection of Public " \
                      "Participation Act (PPPA). This would be ideal, and a legal professional will be able to " \
                      "help you."

        # fill out the statement of defence
        form = FormS2600(self.cid)
        if self.defence.get_defendant() is not None:
            form.defendant = self.defence.get_defendant()
        if self.defence.get_plaintiff() is not None:
            form.plaintiff = self.defence.get_plaintiff()
        if self.defence.get_court_name() is not None:
            form.court_name = self.defence.get_court_name()
        form.claims_unanswered = self.defence.get_withheld()
        form.claims_denied = self.defence.get_denied()
        form.claims_admitted = self.defence.get_agreed()
        if 'apology' in self.defence.data and self.defence.data['apology']['applicable'] is True:
            form.apology_given = True
            form.apology_date = self.defence.data['apology']['date']
            form.apology_method = self.defence.data['apology']['method']
        else:
            form.apology_given = False
        form.was_damaging = self.defence.data.get('is_damaging', None)
        form.was_defamatory = self.defence.data.get('is_defamatory', None)

        defences = self.defence.get_defences()
        defence_paragraphs = []
        fact_paragraphs = []
        for defence in Defence.DEFENCES:
            if defence in defences and defences[defence].applicable is True:
                defence_paragraphs.append(defences[defence].report())
                fact_paragraphs.extend(defences[defence].facts)
        form.set_defences(defence_paragraphs)
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

        # advice for next steps
        offer_advice = False
        if offer_advice:
            lawyer_name = "XYZ incorporated"
            lawyer_site = "https://example.com"
            report += "\n\nThe above documents are as far as I can take you. For additional support, I would recommend connecting with a legal representative from [{site}]({name}). Good luck to you!".format(name=lawyer_name, site=lawyer_site)

        self.response['speech'] = report
        self.response['displayText'] = report

    def reset(self):
        self.defence.reset()

    def save(self):
        self.defence.save()

    def get_response(self):
        return self.response
