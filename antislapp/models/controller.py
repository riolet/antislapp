import re
from antislapp import index
from antislapp.models.defence import Defence
from antislapp.models.formS2600 import FormS2600
from antislapp.models.suitsteps import SuitSteps
from antislapp.models.definitions import definitions


class Controller:
    """
    Invoked by pages/fulfill.
    Responsibilities include:
        Having a function that handles the request that comes out of fulfill
        Building a response
        Organizing any other classes involved. Generally just Defence, but sometimes a form or definition
    """
    def __init__(self, conversation_id, default_response):
        self.cid = conversation_id
        self.domain = "https://antislapp.ca"
        self.default = default_response
        self.defence = Defence(index.db, self.cid)
        self.response = {
            'speech': default_response,
            'displayText': default_response,
            # 'followupEvent': {"name":"<event_name>","data":{"<parameter_name>":"<parameter_value>"}},
            # 'data': _,
            # 'contextOut': [{"name":"weather", "lifespan":2, "parameters":{"city":"Rome"}}],
            #                         contextOut['name'] must be lowercase
            'source': 'riobot',
        }
        self.event_triggers = {
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
            'check-agreed': 'trigger-pleas-true',
            'check-denied': 'trigger-pleas-false',
            'check-withheld': 'trigger-pleas-none',
        }

    def set_sued(self, sued, plaintiff):
        self.defence.sued = sued
        if plaintiff is not None:
            self.defence.plaintiff = plaintiff
        self.set_next_step()
        if sued:
            preface = "There are a few ways to respond to a suit, including trying to settle, or blame someone else." \
                      " This AI will walk you through putting together a \"Statement of Defence.\" That's the next " \
                      "step for defending yourself in court."
        else:
            preface = "Ok, we'll continue as a hypothetical scenario. This AI can walk you through putting together " \
                      "a \"Statement of Defence.\" That's the next step towards you defending yourself in court."
        self.response.get('followupEvent', {}).get('data', {})['preface'] = preface

    def set_defendant(self, name):
        self.defence.defendant = name

    def set_allegations_agree(self, empty, allegation_string):
        if empty:
            self.defence.agreed = []
        else:
            self.defence.agreed = Controller.group_ranges(Controller.string_to_numbers(allegation_string))
        self.set_next_step()

    def set_allegations_deny(self, empty, allegation_string):
        if empty:
            self.defence.denied = []
        else:
            self.defence.denied = Controller.group_ranges(Controller.string_to_numbers(allegation_string))
        self.set_next_step()

    def set_allegations_withhold(self, empty, allegation_string):
        if empty:
            self.defence.withheld = []
        else:
            self.defence.withheld = Controller.group_ranges(Controller.string_to_numbers(allegation_string))
        self.set_next_step()

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
                'name': self.event_triggers[step],
                'data': data
            }
        self.response.pop('speech', None)  # required to be absent
        self.response.pop('displayText', None)  # required to be absent

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

    def set_defamatory(self, defamatory):
        self.defence.defamatory = defamatory
        self.set_next_step()

    def set_damaging(self, damaging):
        self.defence.damaging = damaging
        self.set_next_step()

    def set_apology(self, params):
        self.defence.set_apology(params['happened'], params['date'], params['method'])
        self.set_next_step()

    def set_antislapp(self, ontario, public):
        self.defence.antislapp = ontario and public
        self.set_next_step()

    def set_court_name(self, court_name):
        self.defence.court_name = court_name
        self.set_next_step()

    def boolean_answer(self, context, answer):
        defence = context['parameters']['defence']
        info = {
            'question': context['parameters']['question'],
            'answer': answer
        }
        self.defence.update_defence(defence, info)
        self.set_next_step()

    @staticmethod
    def string_to_numbers(string):
        matches = re.findall(r'\d+\s*-+\s*\d+|\d+\s*\.\.+\s*\d+|\d+', string)
        print("string matches: {}".format(matches))
        numbers = []
        for m in matches:
            try:
                numbers.append(int(float(m)))
                continue
            except:
                pass
            # ranges of form 1..3 or 1-3 with spaces anywhere
            match = re.match(r'\s*(\d+)\s*(?:-+|\.\.+)\s*(\d+)\s*', m)
            if match:
                a = int(match.group(1))
                b = int(match.group(2))
                numbers.extend(range(min(a, b), max(a, b) + 1))
        return numbers

    def get_missing_numbers(self, num_list):
        num_list = set(num_list)
        highest = max(num_list)
        missing = []
        for i in range(1, highest):
            if i not in num_list:
                missing.append(i)
        groups = self.group_ranges(missing)
        return groups

    @staticmethod
    def group_ranges(numbers):
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
        paragraphs = ", ".join(self.defence.denied + self.defence.agreed + self.defence.withheld)
        paragraph_numbers = Controller.string_to_numbers(paragraphs)
        missing_paragraphs = self.get_missing_numbers(paragraph_numbers)
        if missing_paragraphs:
            report += "\n\nSome paragraph numbers ({}) of allegations made seem to be missing. It is important that " \
                      "all allegation paragraphs are accounted for in paragraphs 1, 2, or 3 of Part 1 Division 1 in " \
                      "your defence below.".format(index.join_list(missing_paragraphs))

        # If antislapp legislation applies, mention that!
        if self.defence.antislapp is True:
            report += "\n\nSince you're being sued in Ontario, and it's about a matter of public interest, you can " \
                      "request the court dismiss the proceeding in accordance with the Protection of Public " \
                      "Participation Act (PPPA). This would be ideal, and a legal professional will be able to " \
                      "help you."

        # fill out the statement of defence
        form = FormS2600(self.cid)
        if self.defence.defendant is not None:
            form.defendant = self.defence.defendant
        if self.defence.plaintiff is not None:
            form.plaintiff = self.defence.plaintiff
        if self.defence.court_name is not None:
            form.court_name = self.defence.court_name
        form.claims_unanswered = self.defence.withheld
        form.claims_denied = self.defence.denied
        form.claims_admitted = self.defence.agreed
        form.apology_given, form.apology_date, form.apology_method = self.defence.get_apology()
        form.was_damaging = self.defence.damaging
        form.was_defamatory = self.defence.defamatory

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
                          "[{}](here).".format(form.get_link())

        # steps
        steps = SuitSteps(self.cid)
        steps.populate(self.defence)
        steps.write()
        report = report + "\n\nDownload your Defence Guide " \
                          "[{}](here).".format(steps.get_link())

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
