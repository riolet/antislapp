from antislapp import index
from antislapp.models import controller

conversation = 'abc123'
def_response = 'default response'
claim_id1 = 0  # A
claim_id2 = 1  # B
claim_id3 = 2  # C


def test_everything():

    # me: Hello
    # AI: Hello! Welcome to the AntiSLAPP Legal Defender legal aide service. I can help you with your defense against defamation lawsuits. To get started, what is your name?
    # me: Joe
    c = controller.Controller(conversation, def_response)
    c.reset()
    c.set_defendant('Joe')
    c.save()
    response = c.get_response()
    del c
    assert set(response.keys()) == {'speech', 'displayText', 'source'}
    assert response['speech'] == def_response

    # AI: Pleased to meet you Joe. Now, have you been sued?
    # me: Yes.
    # AI: Who was it that sued you?
    # me: Bob.
    c = controller.Controller(conversation, def_response)
    c.set_sued('true', 'Bob')
    c.save()
    response = c.get_response()
    del c
    assert set(response.keys()) == {'speech', 'displayText', 'source'}
    assert response['speech'] == def_response

    # AI: There are a few ways to respond to a suit...Can you list the specific things they are suing you for in their statement of claim?...
    # me: issue A
    # AI: What paragraph number(s) did they mention "issue A" in, in the lawsuit?
    # me: 9
    c = controller.Controller(conversation, def_response)
    c.add_allegation('issue A', 9)
    c.save()
    response = c.get_response()
    del c
    assert set(response.keys()) == {'speech', 'displayText', 'source'}
    assert response['speech'] == def_response

    # AI: Ok, I've saved that as "issue A". Are there more allegations?
    # me: issue B
    # AI: What paragraph number(s) did they mention "issue B" in, in the lawsuit?
    # me: 4, 5
    c = controller.Controller(conversation, def_response)
    c.add_allegation('issue B', '4, 5')
    c.save()
    response = c.get_response()
    del c
    assert set(response.keys()) == {'speech', 'displayText', 'source'}
    assert response['speech'] == def_response

    # AI: Ok, I've saved that as "issue B". Are there more allegations?
    # me: issue C
    # AI: What paragraph number(s) did they mention "issue C" in, in the lawsuit?
    # me: 6
    c = controller.Controller(conversation, def_response)
    c.add_allegation('issue C', 6)
    c.save()
    response = c.get_response()
    del c
    assert set(response.keys()) == {'speech', 'displayText', 'source'}
    assert response['speech'] == def_response

    # AI: Ok, I've saved that as "issue B". Are there more allegations?
    # me: No
    c = controller.Controller(conversation, def_response)
    c.set_next_step()
    c.save()
    response = c.get_response()
    del c
    assert set(response.keys()) == {'source', 'followupEvent', 'contextOut'}
    assert response['followupEvent'] == {'data': {}, 'name': 'trigger-plead'}
    assert response['contextOut'] == [{'lifespan': 20,
                                       'name': 'currentacc',
                                       'parameters': {'allegation': 'issue A', 'claim_id': claim_id1}}]

    # AI: Do you accept, deny, or are you unable to answer the allegation of "issue A"?
    # me: accept
    c = controller.Controller(conversation, def_response)
    context = {u'lifespan': 19,
               u'name': u'currentacc',
               u'parameters': {u'allegation': u'issue A',
                               u'claim_id': float(claim_id1),
                               u'plead': u'agree',
                               u'plead.original': u''}
    }
    parameters = {u'plead': u'agree'}
    c.make_plea(context, parameters)
    c.save()
    response = c.get_response()
    del c
    del context
    del parameters
    assert set(response.keys()) == {'source', 'followupEvent', 'contextOut'}
    assert response['followupEvent'] == {'data': {}, 'name': 'trigger-plead'}
    assert response['contextOut'] == [{'lifespan': 20,
                                       'name': 'currentacc',
                                       'parameters': {'allegation': 'issue B', 'claim_id': claim_id2}}]

    # AI: Do you accept, deny, or are you unable to answer the allegation of "issue B"?
    # me: can't answer
    c = controller.Controller(conversation, def_response)
    context = {u'lifespan': 19,
               u'name': u'currentacc',
               u'parameters': {u'allegation': u'issue B',
                               u'claim_id': float(claim_id2),
                               u'plead': u'withhold',
                               u'plead.original': u''}
    }
    parameters = {u'plead': u'withhold'}
    c.make_plea(context, parameters)
    c.save()
    response = c.get_response()
    del c
    del context
    del parameters
    assert set(response.keys()) == {'source', 'followupEvent', 'contextOut'}
    assert response['followupEvent'] == {'data': {}, 'name': 'trigger-plead'}
    assert response['contextOut'] == [{'lifespan': 20,
                                       'name': 'currentacc',
                                       'parameters': {'allegation': 'issue C', 'claim_id': claim_id3}}]

    # AI: Do you accept, deny, or are you unable to answer the allegation of "issue B"?
    # me: deny
    c = controller.Controller(conversation, def_response)
    context = {u'lifespan': 19,
               u'name': u'currentacc',
               u'parameters': {u'allegation': u'issue C',
                               u'claim_id': float(claim_id3),
                               u'plead': u'deny',
                               u'plead.original': u''}
    }
    parameters = {u'plead': u'deny'}
    c.make_plea(context, parameters)
    c.save()
    response = c.get_response()
    del c
    del context
    del parameters
    assert set(response.keys()) == {'source', 'followupEvent', 'contextOut'}
    assert response['followupEvent'] == {'data': {}, 'name': 'trigger-truth'}
    assert response['contextOut'] == [{'lifespan': 20,
                                       'name': 'currentacc',
                                       'parameters': {'allegation': 'issue C', 'claim_id': claim_id3}}]

    
