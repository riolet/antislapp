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
                                       'parameters': {'allegation': 'issue C', 'claim_id': claim_id3, 'defence': 'Truth'}}]

    # AI: Regarding the accusation of "issue A," can you use the Truth defence? This applies if you have facts to support what you said or wrote.
    # me: Yes
    c = controller.Controller(conversation, def_response)
    context = {u'lifespan': 19,
               u'name': u'currentacc',
               u'parameters': {u'allegation': u'issue C',
                               u'applicable': u'true',
                               u'applicable.original': u'',
                               u'claim_id': float(claim_id3),
                               u'plead': u'deny',
                               u'plead.original': u'',
                               u'defence': u'Truth'}
    }
    params = {u'applicable': True}
    c.defence_check(context, params)
    c.save()
    response = c.get_response()
    del c
    del context
    del params
    assert set(response.keys()) == {'source', 'followupEvent', 'contextOut'}
    assert response['followupEvent'] == {'data': {}, 'name': 'trigger-facts'}
    assert response['contextOut'] == [{'lifespan': 20,
                                       'name': 'currentacc',
                                       'parameters': {'allegation': 'issue C', 'claim_id': claim_id3, 'defence': 'Truth'}}]

    # AI: What are the facts that would support the Truth defence? Just the facts here, not any specific evidence at this point. Please list them out one at a time.
    # me: Fact 1
    c = controller.Controller(conversation, def_response)
    context = {u'lifespan': 19,
               u'name': u'currentacc',
               u'parameters': {u'allegation': u'issue C',
                               u'applicable': u'true',
                               u'applicable.original': u'',
                               u'claim_id': float(claim_id3),
                               u'defence': u'Truth',
                               u'fact': u'Fact 1',
                               u'fact.original': u'Fact 1',
                               u'plead': u'deny',
                               u'plead.original': u''}}
    fact = u'Fact 1'
    c.add_fact(context, fact)
    c.save()
    response = c.get_response()
    del c
    del context
    del fact
    assert set(response.keys()) == {'source', 'speech', 'displayText'}
    assert response['speech'] == def_response
    assert response['displayText'] == def_response

    # AI: Ok, I've recorded that as "Fact 1." Do you have any more facts?
    # me: yes
    # AI: what is your fact?
    # me: fact 2
    c = controller.Controller(conversation, def_response)
    context = {u'lifespan': 18,
               u'name': u'currentacc',
               u'parameters': {u'allegation': u'issue C',
                               u'applicable': u'true',
                               u'applicable.original': u'',
                               u'claim_id': float(claim_id3),
                               u'defence': u'Truth',
                               u'fact': u'fact 2',
                               u'fact.original': u'fact 2',
                               u'plead': u'deny',
                               u'plead.original': u''}}
    fact = u'fact 2'
    c.add_fact(context, fact)
    c.save()
    response = c.get_response()
    del c
    del context
    del fact
    assert set(response.keys()) == {'source', 'speech', 'displayText'}
    assert response['speech'] == def_response
    assert response['displayText'] == def_response

    # AI: Ok, I've recorded that as "fact 2." Do you have any more facts?
    # me: no

    c = controller.Controller(conversation, def_response)
    context = {u'lifespan': 17,
               u'name': u'currentacc',
               u'parameters': {u'allegation': u'issue C',
                               u'applicable': u'true',
                               u'applicable.original': u'',
                               u'claim_id': float(claim_id3),
                               u'defence': u'Truth',
                               u'fact': u'fact 2',
                               u'fact.original': u'fact 2',
                               u'plead': u'deny',
                               u'plead.original': u''}}
    c.done_facts(context)
    c.save()
    response = c.get_response()
    del c
    del context
    assert set(response.keys()) == {'source', 'followupEvent', 'contextOut'}
    assert response['followupEvent'] == {'data': {}, 'name': 'trigger-absolute'}
    assert response['contextOut'] == [{'lifespan': 20,
                                       'name': 'currentacc',
                                       'parameters': {'allegation': 'issue C', 'claim_id': claim_id3, 'defence': 'Absolute Privilege'}}]


    # AI: Alright, can you use Absolute Privilege? This defence applies if your words were spoken in a courtroom or parliament where you had the right to speak freely. Usually when participating in a trial.
    # me: no

    c = controller.Controller(conversation, def_response)
    context = {u'lifespan': 19,
              u'name': u'currentacc',
              u'parameters': {u'allegation': u'issue C',
                              u'applicable': u'false',
                              u'applicable.original': u'',
                              u'claim_id': float(claim_id3),
                              u'defence': u'Absolute Privilege',
                              u'plead': u'deny',
                              u'plead.original': u''}}
    params = {u'applicable': False}
    c.defence_check(context, params)
    c.save()
    response = c.get_response()
    del c
    del context
    assert set(response.keys()) == {'source', 'followupEvent', 'contextOut'}
    assert response['followupEvent'] == {'data': {}, 'name': 'trigger-qualified'}
    assert response['contextOut'] == [{'lifespan': 20,
                                       'name': 'currentacc',
                                       'parameters': {'allegation': 'issue C', 'claim_id': claim_id3, 'defence': 'Qualified Privilege'}}]


    # AI: ... Qualified Privilege? ...
    # me: no

    c = controller.Controller(conversation, def_response)
    context = {u'lifespan': 19,
              u'name': u'currentacc',
              u'parameters': {u'allegation': u'issue C',
                              u'applicable': u'false',
                              u'applicable.original': u'',
                              u'claim_id': float(claim_id3),
                              u'defence': u'Qualified Privilege',
                              u'plead': u'deny',
                              u'plead.original': u''}}
    params = {u'applicable': False}
    c.defence_check(context, params)
    c.save()
    response = c.get_response()
    del c
    del context
    assert set(response.keys()) == {'source', 'followupEvent', 'contextOut'}
    assert response['followupEvent'] == {'data': {}, 'name': 'trigger-fair'}
    assert response['contextOut'] == [{'lifespan': 20,
                                       'name': 'currentacc',
                                       'parameters': {'allegation': 'issue C', 'claim_id': claim_id3, 'defence': 'Fair Comment'}}]

    # AI: ... Fair Comment? ...
    # me: Yes
    c = controller.Controller(conversation, def_response)
    context = {u'lifespan': 19,
               u'name': u'currentacc',
               u'parameters': {u'allegation': u'issue C',
                               u'applicable': u'true',
                               u'applicable.original': u'',
                               u'claim_id': float(claim_id3),
                               u'defence': u'Fair Comment',
                               u'fact': u'fact 2',
                               u'fact.original': u'fact 2',
                               u'plead': u'deny',
                               u'plead.original': u''}}
    params = {u'applicable': True}
    c.defence_check(context, params)
    c.save()
    response = c.get_response()
    del c
    del context
    del params
    assert set(response.keys()) == {'source', 'followupEvent', 'contextOut'}
    assert response['followupEvent'] == {'data': {}, 'name': 'trigger-facts'}
    assert response['contextOut'] == [{'lifespan': 20,
                                       'name': 'currentacc',
                                       'parameters': {'allegation': 'issue C', 'claim_id': claim_id3, 'defence': 'Fair Comment'}}]

    # AI: What are the facts that would support the Fair Comment defence? Just the facts here, not any specific evidence at this point. Please list them out one at a time.
    # me: Fact 5
    c = controller.Controller(conversation, def_response)
    context = {u'lifespan': 19,
               u'name': u'currentacc',
               u'parameters': {u'allegation': u'issue C',
                               u'applicable': u'true',
                               u'applicable.original': u'',
                               u'claim_id': float(claim_id3),
                               u'defence': u'Fair Comment',
                               u'fact': u'Fact 5',
                               u'fact.original': u'Fact 5',
                               u'plead': u'deny',
                               u'plead.original': u''}}
    fact = u'Fact 5'
    c.add_fact(context, fact)
    c.save()
    response = c.get_response()
    del c
    del context
    del fact
    assert set(response.keys()) == {'source', 'speech', 'displayText'}
    assert response['speech'] == def_response
    assert response['displayText'] == def_response

    # AI: Ok, I've recorded that as "Fact 5." Do you have any more facts?
    # me: no

    c = controller.Controller(conversation, def_response)
    context = {u'lifespan': 18,
               u'name': u'currentacc',
               u'parameters': {u'allegation': u'issue C',
                               u'applicable': u'true',
                               u'applicable.original': u'',
                               u'claim_id': float(claim_id3),
                               u'defence': u'Fair Comment',
                               u'fact': u'Fact 5',
                               u'fact.original': u'Fact 5',
                               u'plead': u'deny',
                               u'plead.original': u''}}
    c.done_facts(context)
    c.save()
    response = c.get_response()
    del c
    del context
    assert set(response.keys()) == {'source', 'followupEvent', 'contextOut'}
    assert response['followupEvent'] == {'data': {}, 'name': 'trigger-responsible'}
    assert response['contextOut'] == [{'lifespan': 20,
                                       'name': 'currentacc',
                                       'parameters': {'allegation': 'issue C', 'claim_id': claim_id3,
                                                      'defence': 'Responsible Communication'}}]

    # AI: ... Responsible Communication? ...
    # me: yes
    c = controller.Controller(conversation, def_response)
    context = {u'lifespan': 19,
               u'name': u'currentacc',
               u'parameters': {u'allegation': u'issue C',
                               u'applicable': u'true',
                               u'applicable.original': u'',
                               u'claim_id': float(claim_id3),
                               u'defence': u'Responsible Communication',
                               u'fact': u'fact 5',
                               u'fact.original': u'fact 5',
                               u'plead': u'deny',
                               u'plead.original': u''}}
    params = {u'applicable': True}
    c.defence_check(context, params)
    c.save()
    response = c.get_response()
    del c
    del context
    del params
    assert set(response.keys()) == {'source', 'followupEvent', 'contextOut'}
    assert response['followupEvent'] == {'data': {'question': 'This is a special test follow-up question for responsible communication. Are you a human?'}, 'name': 'trigger-bool'}
    assert response['contextOut'] == [{'lifespan': 20,
                                       'name': 'currentacc',
                                       'parameters': {'allegation': 'issue C', 'claim_id': claim_id3,
                                                      'defence': 'Responsible Communication'}}]

    # AI: This is a special test follow-up question...
    # me: no
    c = controller.Controller(conversation, def_response)
    context = {u'lifespan': 19,
              u'name': u'currentacc',
              u'parameters': {u'allegation': u'issue C',
                              u'answer': u'true',
                              u'answer.original': u'',
                              u'claim_id': float(claim_id3),
                              u'defence': u'Responsible Communication',
                              u'question': u'This is a special test follow-up question for responsible communication. Are you a human?',
                              u'question.original': u''}}
    answer = False
    c.boolean_answer(context, answer)
    c.save()
    response = c.get_response()
    del c
    del context
    del answer
    assert set(response.keys()) == {'source', 'followupEvent'}
    assert response['followupEvent'] == {'data': {}, 'name': 'trigger-summary'}

    # AI: in summary...
    c = controller.Controller(conversation, def_response)
    c.report()
    c.save()
    response = c.get_response()
    del c
    assert set(response.keys()) == {'source', 'speech', 'displayText'}
    assert response['speech'] == response['displayText']
    assert response['speech'].count("Download") == 2


