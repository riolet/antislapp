from antislapp.models.defence import Defence
from antislapp import index

db = index.db


def test_get_save():
    d1 = Defence(db, 'convo1')
    d2 = Defence(db, 'convo2')
    d1.reset()
    d1.save()
    d2.reset()
    d2.save()

    d1.add_accusation('libel')
    d2.add_accusation('slander')

    assert d1.get_accusations() == ['libel']
    assert d2.get_accusations() == ['slander']

    d1b = Defence(db, 'convo1')
    d2b = Defence(db, 'convo2')
    assert d1b.get_accusations() == []
    assert d2b.get_accusations() == []

    d1.save()
    d2.save()

    d1c = Defence(db, 'convo1')
    d2c = Defence(db, 'convo2')
    assert d1c.get_accusations() == ['libel']
    assert d2c.get_accusations() == ['slander']

def test_accusations():
    d1 = Defence(db, 'convo1')
    d1.reset()
    d1.save()
    assert d1.get_accusations() == []

    d1.add_accusation('acc1')
    assert d1.get_accusations() == ['acc1']

    d1.add_accusation('acc2')
    assert d1.get_accusations() == ['acc1', 'acc2']

    d1.add_accusation('acc3')
    assert d1.get_accusations() == ['acc1', 'acc2', 'acc3']

    d1b = Defence(db, 'convo1')
    assert d1b.get_accusations() == []

    d1.save()
    d1c = Defence(db, 'convo1')
    assert d1c.get_accusations() == ['acc1', 'acc2', 'acc3']

def test_defences():
    d1 = Defence(db, 'convo1')
    d1.reset()
    d1.save()
    assert d1.get_defences() == {}

    d1.add_defence(0, 'def0-0')
    assert d1.get_defences() == {0: ['def0-0']}

    d1.add_defence(0, 'def0-1')
    assert d1.get_defences() == {0: ['def0-0', 'def0-1']}

    d1.add_defence(1, 'def1-0')
    assert d1.get_defences() == {0: ['def0-0', 'def0-1'], 1: ['def1-0']}

    d1b = Defence(db, 'convo1')
    assert d1b.get_defences() == {}

    d1.save()
    d1c = Defence(db, 'convo1')
    assert d1c.get_defences() == {0: ['def0-0', 'def0-1'], 1: ['def1-0']}

def test_report():
    d1 = Defence(db, 'convo1')
    d1.reset()
    d1.save()
    d1.add_accusation('acc1')
    d1.add_accusation('acc2')
    d1.add_accusation('acc3')
    d1.add_defence(0, 'def0-0')
    d1.add_defence(0, 'def0-1')
    d1.add_defence(1, 'def1-0')

    report = d1.report()
    assert report == "You may have been sued. You are accused of (and plead): 0. acc1 (def0-0, def0-1), 1. acc2 (def1-0), 2. acc3 (No plead)"

    d2 = Defence(db, 'convo2')
    d2.reset()
    d2.save()
    d2.set_sued(True)
    report = d2.report()
    assert report == "You have been sued. You are accused of (and plead): "

    d2.set_sued(False)
    report = d2.report()
    assert report == "You have not been sued. You are accused of (and plead): "
