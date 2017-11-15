from antislapp.models.defence import TruthDefence
from antislapp.models.controller import Controller


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


def test_defendant():
    c = blank_controller()
    assert c.defence.get_defendant() is None
    c.set_defendant('Test User')
    assert c.defence.get_defendant() == 'Test User'


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
        'followupEvent': {'name': 'trigger-exit-deny', 'data': {'preface': ' '}},
        'contextOut': [{'lifespan': 20, 'name': 'currentacc', 'parameters': {}}]
    }
    acc_id = c.add_allegation('accu1', 4)
    c.set_next_step()
    resp = c.get_response()
    assert resp['followupEvent'] == {'name': 'trigger-plead', 'data': {'preface': ' '}}
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
        'followupEvent': {'name': 'trigger-plead', 'data': {'preface': ' '}},
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
        'followupEvent': {'name': 'trigger-exit-deny', 'data': {'preface': ' '}},
        'contextOut': [{'lifespan': 20, 'name': 'currentacc', 'parameters': {}}]
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
        'followupEvent': {'name': 'trigger-truth', 'data': {'preface': ' '}},
        'contextOut': [{
            'name': 'currentacc',
            'lifespan': 20,
            'parameters': {
                'paragraphs': '4',
                'defence': 'Truth',
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
        'followupEvent': {'name': 'trigger-absolute', 'data': {'preface': "I've left out the Truth defence."}},
        'contextOut': [{
            'name': 'currentacc',
            'lifespan': 20,
            'parameters': {
                'paragraphs': '4',
                'defence': 'Absolute Privilege',
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
        'followupEvent': {'name': 'trigger-bool', 'data': {'preface': ' ', 'question': 'So everything you stated was fact, or can be proven by facts?'}},
        'contextOut': [{
            'name': 'currentacc',
            'lifespan': 20,
            'parameters': {
                'paragraphs': '4',
                'defence': 'Truth'
            }
        }]
    }


def test_facts():
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
    c.defence.update_defence('Truth', {})

    context = {'parameters': {
        'claim_id': acc_id,
        'allegation': 'accu1',
        'defence': 'Truth'}
    }
    params = {'applicable': True}
    TD = TruthDefence({})
    c.defence_check(context, params)
    c.defence.update_defence('Truth', {'question': TD.extra_questions[0], 'answer': True})
    c.defence.update_defence('Truth', {'question': TD.extra_questions[1], 'answer': True})
    c.defence.update_defence('Truth', {'question': TD.extra_questions[2], 'answer': True})
    c.set_next_step()
    assert c.get_response() == {
        'source': 'riobot',
        'followupEvent': {'name': 'trigger-facts', 'data': {'preface': ' '}},
        'contextOut': [{
            'name': 'currentacc',
            'lifespan': 20,
            'parameters': {
                'paragraphs': '4',
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


def test_defamatory():
    c = blank_controller()
    TD = TruthDefence({})
    cid = c.add_allegation('blah', '1')
    c.make_plea({'parameters': {'claim_id': cid}}, {'plead': 'deny'})
    c.defence_check({'parameters': {'defence': 'Truth'}}, {'applicable': True})
    c.defence.update_defence('Truth', {'question': TD.extra_questions[0], 'answer': True})
    c.defence.update_defence('Truth', {'question': TD.extra_questions[1], 'answer': True})
    c.defence.update_defence('Truth', {'question': TD.extra_questions[2], 'answer': True})
    c.defence_check({'parameters': {'defence': 'Absolute Privilege'}}, {'applicable': False})
    c.defence_check({'parameters': {'defence': 'Qualified Privilege'}}, {'applicable': False})
    c.defence_check({'parameters': {'defence': 'Fair Comment'}}, {'applicable': False})
    c.defence_check({'parameters': {'defence': 'Responsible Communication'}}, {'applicable': False})
    c.done_facts({'parameters': {'defence': 'Truth'}})
    resp = c.get_response()
    assert resp['followupEvent']['name'] == 'trigger-defamatory'
    assert c.defence.get_defamatory() is None
    c.set_defamatory(True)
    assert c.defence.get_defamatory() is True
    c.set_defamatory(False)
    assert c.defence.get_defamatory() is False
    resp = c.get_response()
    assert resp['followupEvent']['name'] == 'trigger-damaging'


def test_damaging():
    c = blank_controller()
    TD = TruthDefence({})
    cid = c.add_allegation('blah', '1')
    c.make_plea({'parameters': {'claim_id': cid}}, {'plead': 'deny'})
    c.defence_check({'parameters': {'defence': 'Truth'}}, {'applicable': True})
    c.defence.update_defence('Truth', {'question': TD.extra_questions[0], 'answer': True})
    c.defence.update_defence('Truth', {'question': TD.extra_questions[1], 'answer': True})
    c.defence.update_defence('Truth', {'question': TD.extra_questions[2], 'answer': True})
    c.defence_check({'parameters': {'defence': 'Absolute Privilege'}}, {'applicable': False})
    c.defence_check({'parameters': {'defence': 'Qualified Privilege'}}, {'applicable': False})
    c.defence_check({'parameters': {'defence': 'Fair Comment'}}, {'applicable': False})
    c.defence_check({'parameters': {'defence': 'Responsible Communication'}}, {'applicable': False})
    c.done_facts({'parameters': {'defence': 'Truth'}})
    c.set_defamatory(True)
    resp = c.get_response()
    assert resp['followupEvent']['name'] == 'trigger-damaging'
    assert c.defence.get_damaging() is None
    c.set_damaging(True)
    assert c.defence.get_damaging() is True
    c.set_damaging(False)
    assert c.defence.get_damaging() is False
    resp = c.get_response()
    assert resp['followupEvent']['name'] == 'trigger-apology'


def test_apology():
    c = blank_controller()
    TD = TruthDefence({})
    cid = c.add_allegation('blah', '1')
    c.make_plea({'parameters': {'claim_id': cid}}, {'plead': 'deny'})
    c.defence_check({'parameters': {'defence': 'Truth'}}, {'applicable': True})
    c.defence.update_defence('Truth', {'question': TD.extra_questions[0], 'answer': True})
    c.defence.update_defence('Truth', {'question': TD.extra_questions[1], 'answer': True})
    c.defence.update_defence('Truth', {'question': TD.extra_questions[2], 'answer': True})
    c.defence_check({'parameters': {'defence': 'Absolute Privilege'}}, {'applicable': False})
    c.defence_check({'parameters': {'defence': 'Qualified Privilege'}}, {'applicable': False})
    c.defence_check({'parameters': {'defence': 'Fair Comment'}}, {'applicable': False})
    c.defence_check({'parameters': {'defence': 'Responsible Communication'}}, {'applicable': False})
    c.done_facts({'parameters': {'defence': 'Truth'}})
    c.set_defamatory(True)
    c.set_damaging(False)
    resp = c.get_response()
    assert resp['followupEvent']['name'] == 'trigger-apology'
    assert c.defence.get_apology() == (False, "", "")
    c.set_apology({'happened': True, 'date': 'TimeA', 'method': 'MethodA'})
    assert c.defence.get_apology() == (True, 'TimeA', 'MethodA')
    c.set_apology({'happened': False, 'date': 'TimeB', 'method': 'MethodB'})
    assert c.defence.get_apology() == (False, "", "")
    resp = c.get_response()
    assert resp['followupEvent']['name'] == 'trigger-court'


def test_court_name():
    c = blank_controller()
    TD = TruthDefence({})
    cid = c.add_allegation('blah', '1')
    c.make_plea({'parameters': {'claim_id': cid}}, {'plead': 'deny'})
    c.defence_check({'parameters': {'defence': 'Truth'}}, {'applicable': True})
    c.defence.update_defence('Truth', {'question': TD.extra_questions[0], 'answer': True})
    c.defence.update_defence('Truth', {'question': TD.extra_questions[1], 'answer': True})
    c.defence.update_defence('Truth', {'question': TD.extra_questions[2], 'answer': True})
    c.defence_check({'parameters': {'defence': 'Absolute Privilege'}}, {'applicable': False})
    c.defence_check({'parameters': {'defence': 'Qualified Privilege'}}, {'applicable': False})
    c.defence_check({'parameters': {'defence': 'Fair Comment'}}, {'applicable': False})
    c.defence_check({'parameters': {'defence': 'Responsible Communication'}}, {'applicable': False})
    c.done_facts({'parameters': {'defence': 'Truth'}})
    c.set_defamatory(True)
    c.set_damaging(False)
    c.set_apology({'happened': True, 'date': 'TimeA', 'method': 'MethodA'})
    resp = c.get_response()
    assert resp['followupEvent']['name'] == 'trigger-court'
    assert c.defence.get_court_name() is None
    court_name = 'Wendigo Court of Sasquatchewan'
    c.set_court_name(court_name)
    assert c.defence.get_court_name() == court_name
    resp = c.get_response()
    assert resp['followupEvent']['name'] == 'trigger-summary'


def test_antislapp():
    c = blank_controller()
    TD = TruthDefence({})
    c.set_sued(True, 'Bad Guy')
    cid = c.add_allegation('blah', '1')
    c.make_plea({'parameters': {'claim_id': cid}}, {'plead': 'deny'})
    c.defence_check({'parameters': {'defence': 'Truth'}}, {'applicable': True})
    c.defence.update_defence('Truth', {'question': TD.extra_questions[0], 'answer': True})
    c.defence.update_defence('Truth', {'question': TD.extra_questions[1], 'answer': True})
    c.defence.update_defence('Truth', {'question': TD.extra_questions[2], 'answer': True})
    c.defence_check({'parameters': {'defence': 'Absolute Privilege'}}, {'applicable': False})
    c.defence_check({'parameters': {'defence': 'Qualified Privilege'}}, {'applicable': False})
    c.defence_check({'parameters': {'defence': 'Fair Comment'}}, {'applicable': False})
    c.defence_check({'parameters': {'defence': 'Responsible Communication'}}, {'applicable': False})
    c.done_facts({'parameters': {'defence': 'Truth'}})
    c.set_defamatory(True)
    c.set_damaging(False)
    c.set_apology({'happened': True, 'date': 'TimeA', 'method': 'MethodA'})
    resp = c.get_response()
    assert resp['followupEvent']['name'] == 'trigger-antislapp'
    assert c.defence.get_antislapp() is None
    c.set_antislapp(False, False)
    assert c.defence.get_antislapp() is False
    c.set_antislapp(True, False)
    assert c.defence.get_antislapp() is False
    c.set_antislapp(False, True)
    assert c.defence.get_antislapp() is False
    c.set_antislapp(True, True)
    assert c.defence.get_antislapp() is True
    resp = c.get_response()
    assert resp['followupEvent']['name'] == 'trigger-court'


def test_boolean():
    c = blank_controller()
    TD = TruthDefence({})
    c.set_sued(True, 'Bad Guy')
    cid = c.add_allegation('blah', '1')
    c.make_plea({'parameters': {'claim_id': cid}}, {'plead': 'deny'})
    c.defence_check({'parameters': {'defence': 'Truth'}}, {'applicable': True})
    resp = c.get_response()
    assert resp['followupEvent']['name'] == 'trigger-bool'
    t = c.defence.get_defences()['Truth']
    assert t.extra_answers == [None, None, None]
    c.boolean_answer({'parameters': {'defence': 'Truth', 'question': TD.extra_questions[0]}}, True)
    t = c.defence.get_defences()['Truth']
    assert t.extra_answers == [True, None, None]
    c.boolean_answer({'parameters': {'defence': 'Truth', 'question': TD.extra_questions[1]}}, False)
    t = c.defence.get_defences()['Truth']
    assert t.extra_answers == [True, False, None]
    c.boolean_answer({'parameters': {'defence': 'Truth', 'question': TD.extra_questions[2]}}, 'skip')
    t = c.defence.get_defences()['Truth']
    assert t.extra_answers == [True, False, 'skip']
    resp = c.get_response()
    assert resp['followupEvent']['name'] == 'trigger-absolute'


def test_get_missing_numbers():
    c = blank_controller()
    assert c.get_missing_numbers([1, 2, 4]) == ['3']
    assert c.get_missing_numbers([1, 2.0, 4.0, 7]) == ['3', '5-6']
    assert c.get_missing_numbers(['1', '3.0', '6', '10']) == ['2', '4-5', '7-9']
    assert c.get_missing_numbers(['1']) == []
    assert c.get_missing_numbers(['1-3', '6..10', '14, 16']) == ['4-5', '11-13', '15']
    assert c.get_missing_numbers([2, 4.0, '8-16', '18', '6, 20..20']) == ['1', '3', '5', '7', '17', '19']


def test_group_ranges():
    c = blank_controller()
    assert c.group_ranges([3,2,7,6,8]) == ['2-3', '6-8']
    assert c.group_ranges([1,2,3,4,6,7,10]) == ['1-4', '6-7', '10']
