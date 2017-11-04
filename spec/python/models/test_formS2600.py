import os
from antislapp.models import formS2600


def test_header():
    form = formS2600.FormS2600('test_header')

    form.defendant = "Joe Pelz"
    form.plaintiff = "Zlep Eoj Legal Firm"
    form.court_name = "The Supreme Court of British Columbia"

    if not os.path.exists(os.path.dirname(form.path)):
        os.makedirs(os.path.dirname(form.path))
    form.writer.append(form.build_header())
    form.writer.write()

def test_footer():
    form = formS2600.FormS2600('test_footer')

    form.defendant = "Joe Pelz"

    if not os.path.exists(os.path.dirname(form.path)):
        os.makedirs(os.path.dirname(form.path))
    form.writer.append(form.build_footer())
    form.writer.write()

def test_body():
    form = formS2600.FormS2600('test_body')

    form.defendant = "Joe Pelz"
    form.was_damaging = False
    form.was_defamatory = False
    form.apology_given = True
    form.apology_date = 'October 22, 2017'
    form.apology_method = 'newspaper ad'
    form.claims_admitted = [{'paragraph': 4}, {'paragraph': 5}, {'paragraph': 6}]
    form.claims_unanswered = [{'paragraph': 9}, {'paragraph': 8}]
    form.claims_denied = [{'paragraph': 7}, {'paragraph': 10}, {'paragraph': 11}]

    if not os.path.exists(os.path.dirname(form.path)):
        os.makedirs(os.path.dirname(form.path))
    form.writer.append(form.build_part1())
    form.writer.append(form.build_part2())
    form.writer.append(form.build_part3())
    form.writer.write()

def test_combination():
    form = formS2600.FormS2600('test_all')

    form.defendant = "Joe Pelz"
    form.plaintiff = "Zlep Eoj Legal Firm"
    form.court_name = "The Supreme Court of British Columbia"
    form.was_damaging = False
    form.was_defamatory = False
    form.apology_given = True
    form.apology_date = 'October 22, 2017'
    form.apology_method = 'newspaper ad'
    form.claims_admitted = [{'paragraph': 4}, {'paragraph': 5}, {'paragraph': 6}]
    form.claims_unanswered = [{'paragraph': 9}, {'paragraph': 8}]
    form.claims_denied = [{'paragraph': 7}, {'paragraph': 10}, {'paragraph': 11}]

    if not os.path.exists(os.path.dirname(form.path)):
        os.makedirs(os.path.dirname(form.path))

    form.writer.append(form.build_header())
    form.writer.append(form.build_part1())
    form.writer.append(form.build_part2())
    form.writer.append(form.build_part3())
    form.writer.append(form.build_footer())
    form.writer.write()