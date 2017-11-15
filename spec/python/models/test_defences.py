import pytest
from antislapp.models.defence import Defence, ResponsibleDefence, AbsoluteDefence, QualifiedDefence
from antislapp import index


db = index.db


def test_save():
    d1 = Defence(db, 'convo1')
    d2 = Defence(db, 'convo2')
    d1.reset()
    d1.save()
    d2.reset()
    d2.save()

    d1.add_allegation('libel', 4)
    d2.add_allegation('slander', 5)

    d1acc = [acc['allegation'] for acc in d1.get_claims()]
    d2acc = [acc['allegation'] for acc in d2.get_claims()]
    assert d1acc == ['libel']
    assert d2acc == ['slander']

    d1b = Defence(db, 'convo1')
    d2b = Defence(db, 'convo2')
    assert d1b.get_claims() == []
    assert d2b.get_claims() == []

    d1.save()
    d2.save()

    d1c = Defence(db, 'convo1')
    d2c = Defence(db, 'convo2')
    d1cacc = [acc['allegation'] for acc in d1c.get_claims()]
    d2cacc = [acc['allegation'] for acc in d2c.get_claims()]
    assert d1cacc == ['libel']
    assert d2cacc == ['slander']


def test_sued():
    d1 = Defence(db, 'convo1')
    d1.reset()
    d1.save()
    assert d1.report() == "In summary, you may have been sued."
    d1.sued = True
    assert d1.report() == "In summary, you have been sued."
    d1.sued = False
    assert d1.report() == "In summary, you have not been sued."


def test_accusations():
    d1 = Defence(db, 'convo1')
    d1.reset()
    d1.save()
    d1acc = [acc['allegation'] for acc in d1.get_claims()]
    assert d1acc == []

    d1.add_allegation('acc1', 4)
    d1acc = [acc['allegation'] for acc in d1.get_claims()]
    assert d1acc == ['acc1']

    d1.add_allegation('acc2', 5)
    d1acc = [acc['allegation'] for acc in d1.get_claims()]
    assert d1acc == ['acc1', 'acc2']

    d1.add_allegation('acc3', 6)
    d1acc = [acc['allegation'] for acc in d1.get_claims()]
    assert d1acc == ['acc1', 'acc2', 'acc3']

    d1b = Defence(db, 'convo1')
    assert d1b.get_claims() == []

    d1.save()
    d1c = Defence(db, 'convo1')
    d1cacc = [acc['allegation'] for acc in d1c.get_claims()]
    assert d1cacc == ['acc1', 'acc2', 'acc3']


def test_plead():
    d1 = Defence(db, 'convo1')
    d1.reset()
    d1.save()
    with pytest.raises(IndexError):
        d1.plead(0, "agree")

    acc1 = d1.add_allegation("acc1", 4)
    with pytest.raises(ValueError):
        d1.plead(acc1, "dook")

    acc2 = d1.add_allegation('acc2', 5)
    acc3 = d1.add_allegation('acc3', 6)
    d1.plead(acc1, "agree")
    d1.plead(acc2, "deny")
    d1.plead(acc3, "withhold")
    accs = d1.get_claims()
    assert accs == [
        {'allegation': 'acc1', 'paragraph': 4, 'plead': 'agree'},
        {'allegation': 'acc2', 'paragraph': 5, 'plead': 'deny'},
        {'allegation': 'acc3', 'paragraph': 6, 'plead': 'withhold'},
    ]


def test_defence():
    d1 = Defence(db, 'convo1')
    d1.reset()
    d1.save()

    with pytest.raises(ValueError):
        d1.add_defence('AboveTheLaw', True)

    ds = d1.get_defences()
    assert 'Truth' not in ds
    d1.add_defence('Truth', 'true')
    ds = d1.get_defences()
    assert 'Truth' in ds
    assert ds['Truth'].applicable is True

    d1.add_defence('Truth', 'false')
    ds = d1.get_defences()
    assert 'Truth' in ds
    assert ds['Truth'].applicable is True

    d1.add_defence('Truth', False)
    ds = d1.get_defences()
    assert 'Truth' in ds
    assert ds['Truth'].applicable is False

    d1.add_defence('Absolute Privilege', False)
    d1.add_defence('Qualified Privilege', False)
    d1.add_defence('Fair Comment', False)
    d1.add_defence('Responsible Communication', False)
    ds = d1.get_defences()
    assert 'Truth' in ds
    assert 'Absolute Privilege' in ds
    assert 'Qualified Privilege' in ds
    assert 'Fair Comment' in ds
    assert 'Responsible Communication' in ds


def test_facts():
    d1 = Defence(db, 'convo1')
    d1.reset()
    d1.save()
    d1.add_defence('Truth', True)
    d1.add_defence('Fair Comment', True)

    with pytest.raises(KeyError):
        d1.add_fact('AboveTheLaw', 'she said he said')

    d1.add_fact('Truth', 'exhibit A')
    d1.add_fact('Truth', 'exhibit B')
    d1.add_fact('Truth', 'exhibit C')
    ds = d1.get_defences()
    d = ds['Truth']
    assert d.applicable is True
    assert d.facts == ['exhibit A', 'exhibit B', 'exhibit C']


def test_get_pleads():
    d1 = Defence(db, 'convo1')
    d1.reset()
    d1.save()
    acc1 = d1.add_allegation("acc1", 4)
    acc2 = d1.add_allegation("acc2", 5)
    acc3 = d1.add_allegation("acc3", 6)
    acc4 = d1.add_allegation("acc4", 7)
    d1.plead(acc1, 'agree')
    d1.plead(acc2, 'deny')
    d1.plead(acc3, 'withhold')

    ags = d1.get_agreed()
    dns = d1.get_denied()
    whs = d1.get_withheld()
    assert len(ags) == 1
    assert len(dns) == 1
    assert len(whs) == 2
    assert ags[0]['allegation'] == 'acc1'
    assert dns[0]['allegation'] == 'acc2'
    assert whs[0]['allegation'] == 'acc3'
    assert whs[1]['allegation'] == 'acc4'

    d1.plead(acc1, 'withhold')
    d1.plead(acc2, 'withhold')
    assert d1.get_agreed() == []
    assert d1.get_denied() == []

    d1.plead(acc1, 'deny')
    d1.plead(acc2, 'deny')
    d1.plead(acc3, 'deny')
    d1.plead(acc4, 'deny')
    assert d1.get_withheld() == []


def test_determine_next_defence():
    d1 = Defence(db, 'convo1')
    d1.reset()
    d1.save()
    assert d1.get_next_step() == {'next_step': 'exit-deny'}

    acw = d1.add_allegation('accW', 4)
    aca = d1.add_allegation('accA', 5)
    ac1 = d1.add_allegation('acc1', 6)
    ac2 = d1.add_allegation('acc2', 7)
    # how do you plead for allegation X?
    assert d1.get_next_step() == {'claim_id': acw, 'allegation': 'accW', 'next_step': 'plead'}
    d1.plead(acw, 'withhold')
    assert d1.get_next_step() == {'claim_id': aca, 'allegation': 'accA', 'next_step': 'plead'}
    d1.plead(aca, 'agree')
    assert d1.get_next_step() == {'claim_id': ac1, 'allegation': 'acc1', 'next_step': 'plead'}
    d1.plead(ac1, 'deny')
    d1.plead(ac2, 'deny')

    # does the truth defence apply to the allegations you deny?
    assert d1.get_next_step() == {'data': {'preface': ' '}, 'paragraphs': '6 and 7', 'defence': 'Truth', 'next_step': 'Truth'}

    # No Truth. Does the AP defence apply?
    d1.add_defence('Truth', False)
    assert d1.get_next_step() == {'data': {'preface': "I've left out the Truth defence."}, 'paragraphs': '6 and 7', 'defence': 'Absolute Privilege', 'next_step': 'Absolute Privilege'}

    # yes? I'll ask some followup questions for AP then...
    d1.add_defence('Absolute Privilege', True)
    AD = AbsoluteDefence({})
    assert d1.get_next_step() == {'next_step': 'question', 'defence': 'Absolute Privilege', 'paragraphs': '6 and 7',
                                  'data': {'preface': "I've left out the Truth defence.",
                                           'question': AD.extra_questions[0]}}
    d1.update_defence('Absolute Privilege', {'question': AD.extra_questions[0], 'answer': True})
    assert d1.get_next_step() == {'next_step': 'question', 'defence': 'Absolute Privilege', 'paragraphs': '6 and 7',
                                  'data': {'preface': "I've left out the Truth defence.",
                                           'question': AD.extra_questions[1]}}
    d1.update_defence('Absolute Privilege', {'question': AD.extra_questions[1], 'answer': True})
    assert d1.get_next_step() == {'next_step': 'question', 'defence': 'Absolute Privilege', 'paragraphs': '6 and 7',
                                  'data': {'preface': "I've left out the Truth defence.",
                                           'question': AD.extra_questions[2]}}
    d1.update_defence('Absolute Privilege', {'question': AD.extra_questions[2], 'answer': True})

    # Accepted. Gather any additional facts.
    assert d1.get_next_step() == {'data': {'preface': "I've left out the Truth defence."}, 'paragraphs': '6 and 7', 'defence': 'Absolute Privilege', 'next_step': 'facts'}
    d1.update_defence('Absolute Privilege', {'question': AD.extra_questions[2], 'answer': 'skip'})
    assert d1.get_next_step() == {'data': {'preface': "I've left out the Truth defence."}, 'paragraphs': '6 and 7', 'defence': 'Absolute Privilege', 'next_step': 'facts'}


    d1.done_facts('Absolute Privilege')
    assert d1.get_next_step() == {'data': {'preface': "Great, I've attached the Absolute Privilege defence to your statement."},
                                  'paragraphs': '6 and 7', 'defence': 'Qualified Privilege', 'next_step': 'Qualified Privilege'}

    d1.add_defence('Qualified Privilege', True)
    QD = QualifiedDefence({})
    assert d1.get_next_step() == {'next_step': 'question', 'defence': 'Qualified Privilege', 'paragraphs': '6 and 7',
                                  'data': {'preface': "Great, I've attached the Absolute Privilege defence to your statement.",
                                           'question': QD.extra_questions[0]}}
    d1.update_defence('Qualified Privilege', {'question': QD.extra_questions[0], 'answer': True})
    d1.update_defence('Qualified Privilege', {'question': QD.extra_questions[1], 'answer': False})
    d1.update_defence('Qualified Privilege', {'question': QD.extra_questions[2], 'answer': False})
    assert d1.get_defences()['Qualified Privilege'].applicable is False

    assert d1.get_next_step() == {'data': {'preface': "I've left out the Qualified Privilege defence."}, 'paragraphs': '6 and 7', 'defence': 'Fair Comment', 'next_step': 'Fair Comment'}
    d1.add_defence('Fair Comment', False)
    assert d1.get_next_step() == {'data': {'preface': "I've left out the Fair Comment defence."}, 'paragraphs': '6 and 7', 'defence': 'Responsible Communication', 'next_step': 'Responsible Communication'}

    d1.add_defence('Responsible Communication', False)
    assert d1.get_next_step() == {'data': {'preface': "I've left out the Responsible Communication defence."},
                                  'next_step': 'check-defamatory'}

    d1.defamatory = True
    print("defamatory: ", d1.defamatory)
    print("data: {}".format(d1.data))
    assert d1.get_next_step() == {'next_step': 'check-damaging'}

    d1.damaging = False
    assert d1.get_next_step() == {'next_step': 'check-apology'}

    d1.set_apology(True, '2017-05-17', 'the newspaper')
    assert d1.get_next_step() == {'next_step': 'check-court'}

    d1.court_name = 'Wendigo Court of Sasquatchewan'
    assert d1.get_next_step() is None

    d1.sued = True
    assert d1.get_next_step() == {'next_step': 'check-antislapp'}

    d1.antislapp = True
    assert d1.get_next_step() is None


def test_resp_comm():
    resp_comm = ResponsibleDefence({})
    d1 = Defence(db, 'convo1')
    d1.reset()
    d1.save()
    ac1 = d1.add_allegation('issue A', 4)
    d1.plead(ac1, 'deny')
    d1.add_defence('Truth', False)
    d1.add_defence('Absolute Privilege', False)
    d1.add_defence('Qualified Privilege', False)
    d1.add_defence('Fair Comment', False)
    d1.add_defence('Responsible Communication', True)

    expected = {
        'paragraphs': '4',
        'defence': 'Responsible Communication',
        'next_step': 'question',
        'data': {'preface': "I've left out the Fair Comment defence.", 'question': resp_comm.extra_questions[0]},
    }
    assert d1.get_next_step() == expected
    d1.update_defence('Responsible Communication', {'question': resp_comm.extra_questions[0], 'answer': True})
    d1.save()

    d1 = Defence(db, 'convo1')
    expected['data']['question'] = resp_comm.extra_questions[1]
    assert d1.get_next_step() == expected
    d1.update_defence('Responsible Communication', {'question': resp_comm.extra_questions[1], 'answer': False})
    d1.save()

    d1 = Defence(db, 'convo1')
    expected['data']['question'] = resp_comm.extra_questions[2]
    assert d1.get_next_step() == expected
    d1.update_defence('Responsible Communication', {'question': resp_comm.extra_questions[2], 'answer': True})
    d1.save()

    d1 = Defence(db, 'convo1')
    expected['data']['question'] = resp_comm.extra_questions[3]
    assert d1.get_next_step() == expected
    d1.update_defence('Responsible Communication', {'question': resp_comm.extra_questions[3], 'answer': 'skip'})
    d1.update_defence('Responsible Communication', {'question': resp_comm.extra_questions[4], 'answer': True})
    d1.update_defence('Responsible Communication', {'question': resp_comm.extra_questions[5], 'answer': 'skip'})
    d1.update_defence('Responsible Communication', {'question': resp_comm.extra_questions[6], 'answer': False})
    d1.save()

    d1 = Defence(db, 'convo1')
    expected = {
        'paragraphs': '4',
        'defence': 'Responsible Communication',
        'next_step': 'facts',
        'data': {'preface': "I've left out the Fair Comment defence."},
    }
    assert d1.get_next_step() == expected
    rc = d1.get_defences()['Responsible Communication']
    assert rc.applicable == True
    d1.update_defence('Responsible Communication', {'question': resp_comm.extra_questions[3], 'answer': False})
    assert rc.applicable == False


def test_report():
    d1 = Defence(db, 'convo1')
    d1.reset()
    d1.save()
    acw = d1.add_allegation('accW', 4)
    aca = d1.add_allegation('accA', 5)
    ac1 = d1.add_allegation('acc1', 6)
    ac2 = d1.add_allegation('acc2', 7)
    d1.plead(acw, 'withhold')
    d1.plead(aca, 'agree')
    d1.plead(ac1, 'deny')
    d1.plead(ac2, 'deny')
    d1.add_defence('Truth', True)
    d1.add_defence('Absolute Privilege', False)
    d1.add_defence('Qualified Privilege', True)
    d1.add_defence('Fair Comment', True)
    d1.add_defence('Responsible Communication', False)

    report = d1.report()
    assert report == 'In summary, you may have been sued. You agree with the claims in paragraphs 5. You deny the ' \
                     'allegations in paragraphs 6 and 7. You cannot respond to claims in paragraphs 4.'

    d2 = Defence(db, 'convo2')
    d2.reset()
    d2.save()
    d2.sued = True
    report = d2.report()
    assert report == "In summary, you have been sued."

    d2.sued = False
    report = d2.report()
    assert report == "In summary, you have not been sued."
