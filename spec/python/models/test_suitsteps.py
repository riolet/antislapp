import os
from antislapp.models import suitsteps


def test_combination():
    form = suitsteps.SuitSteps('test_all')

    form.write()