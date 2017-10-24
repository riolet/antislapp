from antislapp.models.controller import Controller
from antislapp.models.definitions import definitions


def blank_controller():
    c = Controller('convo1', 'def_res')
    c.defence.reset()
    c.defence.save()
    return c


def test_join_list():
    ex = Controller.join_list
    assert ex([]) == ''
    assert ex(['a']) == 'a'
    assert ex(['a', 'b']) == 'a and b'
    assert ex(['a', 'b', 'c']) == 'a, b, and c'
    assert ex(['a', 'b', 'c', 'd']) == 'a, b, c, and d'


def test_sued():
    c = blank_controller()
    assert c.defence.data['sued'] == None
    c.set_sued(True)
    assert c.defence.data['sued'] == True
    c.set_sued(False)
    assert c.defence.data['sued'] == False


def test_add_accusation():
    c = blank_controller()
    assert c.defence.data['claims'] == []
    c.add_accusation('accu1')
    c.add_accusation('accu2')
    c.add_accusation('accu1')
    assert c.defence.data['claims'] == [
        {'accusation': 'accu1'},
        {'accusation': 'accu2'},
        {'accusation': 'accu1'},
    ]


def test_get_definition():
    c = blank_controller()
    c.get_definition('missing_term')
    assert c.get_response() == {
        'speech': "That term isn't in the dictionary",
        'displayText': "That term isn't in the dictionary",
        'source': 'riobot'
    }
    c.get_definition('accused')
    assert c.get_response() == {
        'speech': 'person who is charged with a crime;',
        'displayText': 'person who is charged with a crime;',
        'source': 'riobot'
    }


def test_done_accusations():
    c = blank_controller()
    assert c.get_response() == {
        'speech': 'def_res',
        'displayText': 'def_res',
        'source': 'riobot'
    }
    c.done_accusations()
    assert c.get_response() == {
        'source': 'riobot',
        'followupEvent': {'name': 'trigger-summary', 'data': {}}
    }
    acc_id = c.add_accusation('accu1')
    c.done_accusations()
    assert c.get_response() == {
        'source': 'riobot',
        'followupEvent': {'name': 'trigger-plead', 'data': {}},
        'contextOut': [{
            'name': 'currentacc',
            'lifespan': 2,
            'parameters': {
                'acc': 'accu1',
                'acc_id': acc_id,
                'qst': 'plead'
            }
        }]
    }


def test_make_plea():
    c = blank_controller()
    acc_id = c.add_accusation('accu1')
    context = {
        'acc_id': acc_id
    }
    params = {
        'plead': 'agree'
    }
    c.done_accusations()
    assert c.get_response() == {
        'source': 'riobot',
        'followupEvent': {'name': 'trigger-plead', 'data': {}},
        'contextOut': [{
            'name': 'currentacc',
            'lifespan': 2,
            'parameters': {
                'acc': 'accu1',
                'acc_id': acc_id,
                'qst': 'plead'
            }
        }]
    }
    c.response = {
        'speech': c.default,
        'displayText': c.default,
        'source': 'riobot',
    }
    c.make_plea(context, params)
    c.done_accusations()
    assert c.get_response() == {
        'source': 'riobot',
        'followupEvent': {'name': 'trigger-summary', 'data': {}}
    }


def test_defence_check():
    c = blank_controller()
    acc_id = c.add_accusation('accu1')
    context = {'acc_id': acc_id}
    params = {'plead': 'deny'}
    c.make_plea(context, params)
    c.done_accusations()
    assert c.get_response() == {
        'source': 'riobot',
        'followupEvent': {'name': 'trigger-truth', 'data': {}},
        'contextOut': [{
            'name': 'currentacc',
            'lifespan': 2,
            'parameters': {
                'acc': 'accu1',
                'acc_id': acc_id,
                'qst': 'Truth'
            }
        }]
    }

    context = {'acc_id': acc_id,
               'acc': 'accu1',
               'qst': 'Truth'}
    params = {'valid': False}
    c.defence_check(context, params)
    assert c.get_response() == {
        'source': 'riobot',
        'followupEvent': {'name': 'trigger-absolute', 'data': {}},
        'contextOut': [{
            'name': 'currentacc',
            'lifespan': 2,
            'parameters': {
                'acc': 'accu1',
                'acc_id': acc_id,
                'qst': 'Absolute Privilege'
            }
        }]
    }

    context = {'acc_id': acc_id,
               'acc': 'accu1',
               'qst': 'Truth'}
    params = {'valid': True}
    c.defence_check(context, params)
    assert c.get_response() == {
        'source': 'riobot',
        'followupEvent': {'name': 'trigger-facts', 'data': {}},
        'contextOut': [{
            'name': 'currentacc',
            'lifespan': 2,
            'parameters': {
                'acc': 'accu1',
                'acc_id': acc_id,
                'qst': 'Truth'
            }
        }]
    }


def test_add_facts():
    c = blank_controller()
    acc_id = c.add_accusation('accu1')
    context = {'acc_id': acc_id}
    params = {'plead': 'deny'}
    c.make_plea(context, params)
    context = {'acc_id': acc_id,
               'acc': 'accu1',
               'qst': 'Truth'}
    params = {'valid': True}
    c.defence_check(context, params)

    context = {'acc_id': acc_id,
               'acc': 'accu1',
               'qst': 'Truth'}
    params = {'valid': True}
    c.defence_check(context, params)
    assert c.get_response() == {
        'source': 'riobot',
        'followupEvent': {'name': 'trigger-facts', 'data': {}},
        'contextOut': [{
            'name': 'currentacc',
            'lifespan': 2,
            'parameters': {
                'acc': 'accu1',
                'acc_id': acc_id,
                'qst': 'Truth'
            }
        }]
    }

    context = {'acc_id': acc_id,
               'acc': 'accu1',
               'qst': 'Truth'}
    fact = "fact 1"
    c.response = {
            'speech': c.default,
            'displayText': c.default,
            'source': 'riobot'
    }
    c.add_fact(context, fact)
    assert c.get_response() == {
        'speech': c.default,
        'displayText': c.default,
        'source': 'riobot',
        'contextOut': [{
            'name': 'currentacc',
            'lifespan': 2,
            'parameters': {
                'acc': 'accu1',
                'acc_id': acc_id,
                'qst': 'Truth'
            }
        }]
    }
