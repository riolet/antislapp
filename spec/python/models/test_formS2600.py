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
    form.fax_number = "604 342 7755"
    form.email = "jplegal@example.com"


    if not os.path.exists(os.path.dirname(form.path)):
        os.makedirs(os.path.dirname(form.path))
    form.writer.append(form.build_footer())
    form.writer.write()
