from antislapp.models.controller import Controller
from antislapp.models.definitions import definitions


def blank_controller():
    c = Controller('convo1', 'def_res')
    c.defence.reset()
    c.defence.save()
    return c


def test_sued():
    c = blank_controller()
    assert c.defence.data['sued'] == None
    assert c.defence.get_plaintiff() == None
    c.set_sued(True, 'Bad Guy')
    assert c.defence.data['sued'] == True
    assert c.defence.get_plaintiff() == 'Bad Guy'
    c.set_sued(False, 'Bad Guy2')
    assert c.defence.data['sued'] == False
    assert c.defence.get_plaintiff() == 'Bad Guy2'


def test_add_allegation():
    c = blank_controller()
    assert c.defence.data['claims'] == []
    c.add_allegation('accu1', 4)
    c.add_allegation('accu2', 5)
    c.add_allegation('accu1', 6)
    assert c.defence.data['claims'] == [
        {'allegation': 'accu1', 'paragraph': 4, 'plead': None},
        {'allegation': 'accu2', 'paragraph': 5, 'plead': None},
        {'allegation': 'accu1', 'paragraph': 6, 'plead': None},
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


def test_set_next_step():
    c = blank_controller()
    assert c.get_response() == {
        'speech': 'def_res',
        'displayText': 'def_res',
        'source': 'riobot'
    }
    c.set_next_step()
    assert c.get_response() == {
        'source': 'riobot',
        'followupEvent': {'name': 'trigger-summary', 'data': {}}
    }
    acc_id = c.add_allegation('accu1', 4)
    c.set_next_step()
    resp = c.get_response()
    assert resp['followupEvent'] == {'name': 'trigger-plead', 'data': {}}
    assert resp['contextOut'] == [{
        'name': 'currentacc',
        'lifespan': 20,
        'parameters': {
            'allegation': 'accu1',
            'claim_id': acc_id,
        }
    }]


def test_make_plea():
    c = blank_controller()
    acc_id = c.add_allegation('accu1', 4)
    context = {'parameters': {'claim_id': acc_id}}
    params = {'plead': 'agree'}
    c.set_next_step()
    assert c.get_response() == {
        'source': 'riobot',
        'followupEvent': {'name': 'trigger-plead', 'data': {}},
        'contextOut': [{
            'name': 'currentacc',
            'lifespan': 20,
            'parameters': {
                'allegation': 'accu1',
                'claim_id': acc_id,
            }
        }]
    }
    c.response = {
        'speech': c.default,
        'displayText': c.default,
        'source': 'riobot',
    }
    c.make_plea(context, params)
    c.set_next_step()
    assert c.get_response() == {
        'source': 'riobot',
        'followupEvent': {'name': 'trigger-summary', 'data': {}}
    }


def test_defence_check():
    c = blank_controller()
    acc_id = c.add_allegation('accu1', 4)
    context = {'parameters': {'claim_id': acc_id}}
    params = {'plead': 'deny'}
    c.make_plea(context, params)
    c.set_next_step()
    assert c.get_response() == {
        'source': 'riobot',
        'followupEvent': {'name': 'trigger-truth', 'data': {}},
        'contextOut': [{
            'name': 'currentacc',
            'lifespan': 20,
            'parameters': {
                'allegation': 'accu1',
                'claim_id': acc_id,
                'defence': 'Truth'
            }
        }]
    }

    context = {'parameters': {
        'claim_id': acc_id,
        'allegation': 'accu1',
        'defence': 'Truth'}
    }
    params = {'applicable': False}
    c.defence_check(context, params)
    assert c.get_response() == {
        'source': 'riobot',
        'followupEvent': {'name': 'trigger-absolute', 'data': {}},
        'contextOut': [{
            'name': 'currentacc',
            'lifespan': 20,
            'parameters': {
                'allegation': 'accu1',
                'claim_id': acc_id,
                'defence': 'Absolute Privilege'
            }
        }]
    }

    context = {'parameters': {
        'claim_id': acc_id,
        'allegation': 'accu1',
        'defence': 'Truth'}
    }
    params = {'applicable': True}
    c.defence_check(context, params)
    assert c.get_response() == {
        'source': 'riobot',
        'followupEvent': {'name': 'trigger-facts', 'data': {}},
        'contextOut': [{
            'name': 'currentacc',
            'lifespan': 20,
            'parameters': {
                'allegation': 'accu1',
                'claim_id': acc_id,
                'defence': 'Truth'
            }
        }]
    }


def test_add_facts():
    c = blank_controller()
    acc_id = c.add_allegation('accu1', 4)
    context = {'parameters': {'claim_id': acc_id}}
    params = {'plead': 'deny'}
    c.make_plea(context, params)
    context = {'parameters': {
        'claim_id': acc_id,
        'allegation': 'accu1',
        'defence': 'Truth'}
    }
    params = {'applicable': True}
    c.defence_check(context, params)

    context = {'parameters': {
        'claim_id': acc_id,
        'allegation': 'accu1',
        'defence': 'Truth'}
    }
    params = {'applicable': True}
    c.defence_check(context, params)
    assert c.get_response() == {
        'source': 'riobot',
        'followupEvent': {'name': 'trigger-facts', 'data': {}},
        'contextOut': [{
            'name': 'currentacc',
            'lifespan': 20,
            'parameters': {
                'allegation': 'accu1',
                'claim_id': acc_id,
                'defence': 'Truth'
            }
        }]
    }

    context = {'parameters': {
        'claim_id': acc_id,
        'allegation': 'accu1',
        'defence': 'Truth'}
    }
    fact = "fact 1"
    c.response = {
            'speech': c.default,
            'displayText': c.default,
            'source': 'riobot'
    }
    c.add_fact(context, fact)
    assert c.get_response() == {
        'source': 'riobot',
        'speech': c.default,
        'displayText': c.default,
    }
