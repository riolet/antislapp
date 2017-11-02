import pytest
from antislapp.models.defence import Defence
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
    d1.set_sued(True)
    assert d1.report() == "In summary, you have been sued."
    d1.set_sued(False)
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
    acc1 = d1.add_allegation("acc1", 4)
    with pytest.raises(IndexError):
        d1.add_defence(1000, 'Truth', True)

    with pytest.raises(ValueError):
        d1.add_defence(acc1, 'AboveTheLaw', True)

    d1.add_defence(acc1, 'Truth', 'true')
    a = d1.get_claims()
    assert 'Truth' in a[0]
    assert a[0]['Truth'].applicable is True

    d1.add_defence(acc1, 'Truth', 'false')
    a = d1.get_claims()
    assert 'Truth' in a[0]
    assert a[0]['Truth'].applicable is True

    d1.add_defence(acc1, 'Truth', False)
    a = d1.get_claims()
    assert 'Truth' in a[0]
    assert a[0]['Truth'].applicable is False

    d1.add_defence(acc1, 'Absolute Privilege', False)
    d1.add_defence(acc1, 'Qualified Privilege', False)
    d1.add_defence(acc1, 'Fair Comment', False)
    d1.add_defence(acc1, 'Responsible Communication', False)
    a = d1.get_claims()
    assert 'Truth' in a[0]
    assert 'Absolute Privilege' in a[0]
    assert 'Qualified Privilege' in a[0]
    assert 'Fair Comment' in a[0]
    assert 'Responsible Communication' in a[0]


def test_facts():
    d1 = Defence(db, 'convo1')
    d1.reset()
    d1.save()
    acc1 = d1.add_allegation("acc1", 4)
    d1.add_defence(acc1, 'Truth', True)
    d1.add_defence(acc1, 'Fair Comment', True)
    with pytest.raises(IndexError):
        d1.add_fact(1000, 'Truth', 'he said she said')

    with pytest.raises(ValueError):
        d1.add_fact(acc1, 'AboveTheLaw', 'she said he said')

    d1.add_fact(acc1, 'Truth', 'exhibit A')
    d1.add_fact(acc1, 'Truth', 'exhibit B')
    d1.add_fact(acc1, 'Truth', 'exhibit C')
    a = d1.get_claims()
    d = a[0]['Truth']
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
    assert d1.get_next_step() is None

    acw = d1.add_allegation('accW', 4)
    aca = d1.add_allegation('accA', 5)
    ac1 = d1.add_allegation('acc1', 6)
    ac2 = d1.add_allegation('acc2', 7)
    assert d1.get_next_step() == {'claim_id': acw, 'allegation': 'accW', 'next_step': 'plead'}
    d1.plead(acw, 'withhold')
    assert d1.get_next_step() == {'claim_id': aca, 'allegation': 'accA', 'next_step': 'plead'}
    d1.plead(aca, 'agree')
    assert d1.get_next_step() == {'claim_id': ac1, 'allegation': 'acc1', 'next_step': 'plead'}
    d1.plead(ac1, 'deny')
    d1.plead(ac2, 'deny')

    assert d1.get_next_step() == {'claim_id': ac1, 'allegation': 'acc1', 'defence': 'Truth', 'next_step': 'Truth'}

    d1.add_defence(ac1, 'Truth', False)
    assert d1.get_next_step() == {'claim_id': ac1, 'allegation': 'acc1', 'defence': 'Absolute Privilege', 'next_step': 'Absolute Privilege'}

    d1.add_defence(ac1, 'Absolute Privilege', True)
    assert d1.get_next_step() == {'claim_id': ac1, 'allegation': 'acc1', 'defence': 'Absolute Privilege', 'next_step': 'facts', 'data': {}}
    d1.done_facts(ac1, 'Absolute Privilege')

    d1.add_defence(ac1, 'Qualified Privilege', True)
    d1.done_facts(ac1, 'Qualified Privilege')
    d1.add_defence(ac1, 'Fair Comment', False)
    assert d1.get_next_step() == {'claim_id': ac1, 'allegation': 'acc1', 'defence': 'Responsible Communication', 'next_step': 'Responsible Communication'}

    d1.add_defence(ac1, 'Responsible Communication', False)
    assert d1.get_next_step() == {'claim_id': ac2, 'allegation': 'acc2', 'defence': 'Truth', 'next_step': 'Truth'}

    d1.add_defence(ac2, 'Truth', True)
    assert d1.get_next_step() == {'claim_id': ac2, 'allegation': 'acc2', 'defence': 'Truth', 'next_step': 'facts', 'data': {}}
    d1.done_facts(ac2, 'Truth')
    assert d1.get_next_step() == {'claim_id': ac2, 'allegation': 'acc2', 'defence': 'Absolute Privilege', 'next_step': 'Absolute Privilege'}

    d1.add_defence(ac2, 'Absolute Privilege', False)
    d1.add_defence(ac2, 'Qualified Privilege', False)
    d1.add_defence(ac2, 'Fair Comment', False)
    d1.add_defence(ac2, 'Responsible Communication', False)
    assert d1.get_next_step() is None


def test_resp_comm():
    d1 = Defence(db, 'convo1')
    d1.reset()
    d1.save()
    ac1 = d1.add_allegation('issue A', 4)
    d1.plead(ac1, 'deny')
    d1.add_defence(ac1, 'Truth', False)
    d1.add_defence(ac1, 'Absolute Privilege', False)
    d1.add_defence(ac1, 'Qualified Privilege', False)
    d1.add_defence(ac1, 'Fair Comment', False)
    d1.add_defence(ac1, 'Responsible Communication', True)
    # question edits for simpler testing:
    _temp_ = d1.get_defence(ac1, 'Responsible Communication')
    assert hasattr(_temp_, 'extra_questions')
    assert hasattr(_temp_, 'extra_answers')
    _temp_.extra_questions = ['Question 1', 'Question 2', 'Question 3', 'Question 4']
    _temp_.extra_answers = [None, None, None, None]

    expected = {
        'claim_id': ac1,
        'allegation': 'issue A',
        'defence': 'Responsible Communication',
        'next_step': 'question',
        'data': {'question': 'Question 1'},
    }
    assert d1.get_next_step() == expected

    d1.update_defence(ac1, 'Responsible Communication', {'question': 'Question 1', 'answer': True})
    expected['data']['question'] = 'Question 2'
    assert d1.get_next_step() == expected
    d1.update_defence(ac1, 'Responsible Communication', {'question': 'Question 2', 'answer': False})
    expected['data']['question'] = 'Question 3'
    assert d1.get_next_step() == expected
    d1.update_defence(ac1, 'Responsible Communication', {'question': 'Question 3', 'answer': True})
    expected['data']['question'] = 'Question 4'
    assert d1.get_next_step() == expected
    d1.update_defence(ac1, 'Responsible Communication', {'question': 'Question 4', 'answer': 'skip'})
    assert d1.get_next_step() == None
    rc = d1.get_defence(ac1, 'Responsible Communication')
    assert rc.applicable == True
    d1.update_defence(ac1, 'Responsible Communication', {'question': 'Question 4', 'answer': False})
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
    d1.add_defence(ac1, 'Truth', True)
    d1.add_defence(ac1, 'Absolute Privilege', False)
    d1.add_defence(ac1, 'Qualified Privilege', True)
    d1.add_defence(ac2, 'Fair Comment', True)

    report = d1.report()
    assert report == 'In summary, you may have been sued. You agree with the claims in paragraphs 5. You deny the ' \
                     'allegations in paragraphs 6 and 7. You cannot respond to claims in paragraphs 4.'

    d2 = Defence(db, 'convo2')
    d2.reset()
    d2.save()
    d2.set_sued(True)
    report = d2.report()
    assert report == "In summary, you have been sued."

    d2.set_sued(False)
    report = d2.report()
    assert report == "In summary, you have not been sued."
