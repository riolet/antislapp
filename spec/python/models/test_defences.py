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

    d1.add_accusation('libel')
    d2.add_accusation('slander')

    d1acc = [acc['accusation'] for acc in d1.get_claims()]
    d2acc = [acc['accusation'] for acc in d2.get_claims()]
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
    d1cacc = [acc['accusation'] for acc in d1c.get_claims()]
    d2cacc = [acc['accusation'] for acc in d2c.get_claims()]
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
    d1acc = [acc['accusation'] for acc in d1.get_claims()]
    assert d1acc == []

    d1.add_accusation('acc1')
    d1acc = [acc['accusation'] for acc in d1.get_claims()]
    assert d1acc == ['acc1']

    d1.add_accusation('acc2')
    d1acc = [acc['accusation'] for acc in d1.get_claims()]
    assert d1acc == ['acc1', 'acc2']

    d1.add_accusation('acc3')
    d1acc = [acc['accusation'] for acc in d1.get_claims()]
    assert d1acc == ['acc1', 'acc2', 'acc3']

    d1b = Defence(db, 'convo1')
    assert d1b.get_claims() == []

    d1.save()
    d1c = Defence(db, 'convo1')
    d1cacc = [acc['accusation'] for acc in d1c.get_claims()]
    assert d1cacc == ['acc1', 'acc2', 'acc3']


def test_plead():
    d1 = Defence(db, 'convo1')
    d1.reset()
    d1.save()
    with pytest.raises(IndexError):
        d1.plead(0, "agree")

    acc1 = d1.add_accusation("acc1")
    with pytest.raises(ValueError):
        d1.plead(acc1, "dook")

    acc2 = d1.add_accusation('acc2')
    acc3 = d1.add_accusation('acc3')
    d1.plead(acc1, "agree")
    d1.plead(acc2, "deny")
    d1.plead(acc3, "withhold")
    accs = d1.get_claims()
    assert accs == [
        {'accusation': 'acc1',
         'plead': 'agree'},
        {'accusation': 'acc2',
         'plead': 'deny'},
        {'accusation': 'acc3',
         'plead': 'withhold'},
    ]


def test_defence():
    d1 = Defence(db, 'convo1')
    d1.reset()
    d1.save()
    acc1 = d1.add_accusation("acc1")
    with pytest.raises(IndexError):
        d1.add_defence(1000, 'Truth', True)

    with pytest.raises(ValueError):
        d1.add_defence(acc1, 'AboveTheLaw', True)

    d1.add_defence(acc1, 'Truth', 'true')
    a = d1.get_claims()
    assert 'Truth' in a[0]
    assert a[0]['Truth']['valid'] == True

    d1.add_defence(acc1, 'Truth', 'false')
    a = d1.get_claims()
    assert 'Truth' in a[0]
    assert a[0]['Truth']['valid'] == True

    d1.add_defence(acc1, 'Truth', False)
    a = d1.get_claims()
    assert 'Truth' in a[0]
    assert a[0]['Truth']['valid'] == False

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
    acc1 = d1.add_accusation("acc1")
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
    assert d['valid'] == True
    assert d['facts'] == ['exhibit A', 'exhibit B', 'exhibit C']


def test_get_pleads():
    d1 = Defence(db, 'convo1')
    d1.reset()
    d1.save()
    acc1 = d1.add_accusation("acc1")
    acc2 = d1.add_accusation("acc2")
    acc3 = d1.add_accusation("acc3")
    acc4 = d1.add_accusation("acc4")
    d1.plead(acc1, 'agree')
    d1.plead(acc2, 'deny')
    d1.plead(acc3, 'withhold')

    ags = d1.get_agreed()
    dns = d1.get_denied()
    whs = d1.get_withheld()
    assert len(ags) == 1
    assert len(dns) == 1
    assert len(whs) == 2
    assert ags[0]['accusation'] == 'acc1'
    assert dns[0]['accusation'] == 'acc2'
    assert whs[0]['accusation'] == 'acc3'
    assert whs[1]['accusation'] == 'acc4'

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
    assert d1.determine_next_question() is None

    acw = d1.add_accusation('accW')
    aca = d1.add_accusation('accA')
    ac1 = d1.add_accusation('acc1')
    ac2 = d1.add_accusation('acc2')
    assert d1.determine_next_question() == {'acc_id': acw, 'acc': 'accW', 'qst': 'plead'}
    d1.plead(acw, 'withhold')
    assert d1.determine_next_question() == {'acc_id': aca, 'acc': 'accA', 'qst': 'plead'}
    d1.plead(aca, 'agree')
    assert d1.determine_next_question() == {'acc_id': ac1, 'acc': 'acc1', 'qst': 'plead'}
    d1.plead(ac1, 'deny')
    d1.plead(ac2, 'deny')

    assert d1.determine_next_question() == {'acc_id': ac1, 'acc': 'acc1', 'qst': 'Truth'}

    d1.add_defence(ac1, 'Truth', False)
    assert d1.determine_next_question() == {'acc_id': ac1, 'acc': 'acc1', 'qst': 'Absolute Privilege'}

    d1.add_defence(ac1, 'Absolute Privilege', True)
    assert d1.determine_next_question() == {'acc_id': ac1, 'acc': 'acc1', 'qst': 'Qualified Privilege'}

    d1.add_defence(ac1, 'Qualified Privilege', True)
    d1.add_defence(ac1, 'Fair Comment', False)
    assert d1.determine_next_question() == {'acc_id': ac1, 'acc': 'acc1', 'qst': 'Responsible Communication'}

    d1.add_defence(ac1, 'Responsible Communication', False)
    assert d1.determine_next_question() == {'acc_id': ac2, 'acc': 'acc2', 'qst': 'Truth'}

    d1.add_defence(ac2, 'Truth', True)
    assert d1.determine_next_question() == {'acc_id': ac2, 'acc': 'acc2', 'qst': 'Absolute Privilege'}

    d1.add_defence(ac2, 'Absolute Privilege', False)
    d1.add_defence(ac2, 'Qualified Privilege', False)
    d1.add_defence(ac2, 'Fair Comment', False)
    d1.add_defence(ac2, 'Responsible Communication', False)
    assert d1.determine_next_question() is None


def test_report():
    d1 = Defence(db, 'convo1')
    d1.reset()
    d1.save()
    acw = d1.add_accusation('accW')
    aca = d1.add_accusation('accA')
    ac1 = d1.add_accusation('acc1')
    ac2 = d1.add_accusation('acc2')
    d1.plead(acw, 'withhold')
    d1.plead(aca, 'agree')
    d1.plead(ac1, 'deny')
    d1.plead(ac2, 'deny')
    d1.add_defence(ac1, 'Truth', True)
    d1.add_defence(ac1, 'Absolute Privilege', False)
    d1.add_defence(ac1, 'Qualified Privilege', True)
    d1.add_defence(ac2, 'Fair Comment', True)

    report = d1.report()
    assert report == 'In summary, you may have been sued. You agree with the claims of "accA". ' \
                     'You deny the allegations of "acc1", "acc2". You cannot respond to claims of "accW".'

    d2 = Defence(db, 'convo2')
    d2.reset()
    d2.save()
    d2.set_sued(True)
    report = d2.report()
    assert report == "In summary, you have been sued."

    d2.set_sued(False)
    report = d2.report()
    assert report == "In summary, you have not been sued."
