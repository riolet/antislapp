from antislapp import index
from antislapp.models import controller
from antislapp.models.defence import ResponsibleDefence, TruthDefence, FairCommentDefence

conversation = 'abc123'
def_response = 'default response'
claim_id1 = 0  # A
claim_id2 = 1  # B
claim_id3 = 2  # C


def test_everything():
    TD = TruthDefence({})
    FD = FairCommentDefence({})
    RD = ResponsibleDefence({})
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
    assert response['followupEvent'] == {'data': {'preface': ' '}, 'name': 'trigger-plead'}
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
    assert response['followupEvent'] == {'data': {'preface': ' '}, 'name': 'trigger-plead'}
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
    assert response['followupEvent'] == {'data': {'preface': ' '}, 'name': 'trigger-plead'}
    assert response['contextOut'] == [{'lifespan': 20,
                                       'name': 'currentacc',
                                       'parameters': {'allegation': 'issue C', 'claim_id': claim_id3}}]

    # AI: Do you accept, deny, or are you unable to answer the allegation of "issue C"?
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
    assert response['followupEvent'] == {'data': {'preface': ' '}, 'name': 'trigger-truth'}
    assert response['contextOut'] == [{'lifespan': 20,
                                       'name': 'currentacc',
                                       'parameters': {'paragraphs': '6', 'defence': 'Truth'}}]

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
    assert response['followupEvent'] == {'data': {'preface': ' ', 'question': TD.extra_questions[0]}, 'name': 'trigger-bool'}
    assert response['contextOut'] == [{'lifespan': 20,
                                       'name': 'currentacc',
                                       'parameters': {'paragraphs': '6', 'defence': 'Truth'}}]

    # AI: Truth-extra-question-1?
    # me: Yes
    c = controller.Controller(conversation, def_response)
    context = {'parameters': {
        'defence': 'Truth',
        'question': TD.extra_questions[0]
    }}
    c.boolean_answer(context, True)
    c.save()
    response = c.get_response()
    del c
    del context
    assert set(response.keys()) == {'source', 'followupEvent', 'contextOut'}
    assert response['followupEvent'] == {'data': {'preface': ' ', 'question': TD.extra_questions[1]}, 'name': 'trigger-bool'}
    assert response['contextOut'] == [{'lifespan': 20,
                                       'name': 'currentacc',
                                       'parameters': {'paragraphs': '6', 'defence': 'Truth'}}]

    # AI: Truth-extra-question-2?
    # me: No
    c = controller.Controller(conversation, def_response)
    context = {'parameters': {
        'defence': 'Truth',
        'question': TD.extra_questions[1]
    }}
    c.boolean_answer(context, False)
    c.save()
    response = c.get_response()
    del c
    del context
    assert set(response.keys()) == {'source', 'followupEvent', 'contextOut'}
    assert response['followupEvent'] == {'data': {'preface': ' ', 'question': TD.extra_questions[2]}, 'name': 'trigger-bool'}
    assert response['contextOut'] == [{'lifespan': 20,
                                       'name': 'currentacc',
                                       'parameters': {'paragraphs': '6', 'defence': 'Truth'}}]

    # AI: Truth-extra-question-3?
    # me: skip
    c = controller.Controller(conversation, def_response)
    context = {'parameters': {
        'defence': 'Truth',
        'question': TD.extra_questions[2]
    }}
    c.boolean_answer(context, True)
    c.save()
    response = c.get_response()
    del c
    del context
    assert set(response.keys()) == {'source', 'followupEvent', 'contextOut'}
    assert response['followupEvent'] == {'data': {'preface': ' '}, 'name': 'trigger-facts'}
    assert response['contextOut'] == [{'lifespan': 20,
                                       'name': 'currentacc',
                                       'parameters': {'paragraphs': '6', 'defence': 'Truth'}}]

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
    assert response['followupEvent'] == {'data': {'preface': "Great, I've attached the Truth defence to your statement."}, 'name': 'trigger-absolute'}
    assert response['contextOut'] == [{'lifespan': 20,
                                       'name': 'currentacc',
                                       'parameters': {'paragraphs': '6', 'defence': 'Absolute Privilege'}}]


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
    assert response['followupEvent'] == {'data': {'preface': "I've left out the Absolute Privilege defence."}, 'name': 'trigger-qualified'}
    assert response['contextOut'] == [{'lifespan': 20,
                                       'name': 'currentacc',
                                       'parameters': {'paragraphs': '6', 'defence': 'Qualified Privilege'}}]


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
    assert response['followupEvent'] == {'data': {'preface': "I've left out the Qualified Privilege defence."}, 'name': 'trigger-fair'}
    assert response['contextOut'] == [{'lifespan': 20,
                                       'name': 'currentacc',
                                       'parameters': {'paragraphs': '6', 'defence': 'Fair Comment'}}]

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
    assert response['followupEvent'] == {'data': {'preface': "I've left out the Qualified Privilege defence.",
                                                  'question': FD.extra_questions[0]},
                                         'name': 'trigger-bool'}
    assert response['contextOut'] == [{'lifespan': 20,
                                       'name': 'currentacc',
                                       'parameters': {'paragraphs': '6', 'defence': 'Fair Comment'}}]

    # AI: FD-extra-question-1?
    # me: No
    c = controller.Controller(conversation, def_response)
    context = {'parameters': {
        'defence': 'Fair Comment',
        'question': FD.extra_questions[0]
    }}
    c.boolean_answer(context, False)
    c.save()
    response = c.get_response()
    del c
    del context
    assert set(response.keys()) == {'source', 'followupEvent', 'contextOut'}
    assert response['followupEvent'] == {'data': {'preface': "I've left out the Qualified Privilege defence.",
                                                  'question': FD.extra_questions[1]},
                                         'name': 'trigger-bool'}
    assert response['contextOut'] == [{'lifespan': 20,
                                       'name': 'currentacc',
                                       'parameters': {'paragraphs': '6', 'defence': 'Fair Comment'}}]

    # AI: FD-extra-question-2?
    # me: yes
    c = controller.Controller(conversation, def_response)
    context = {'parameters': {
        'defence': 'Fair Comment',
        'question': FD.extra_questions[1]
    }}
    c.boolean_answer(context, False)
    c.save()
    response = c.get_response()
    del c
    del context
    assert set(response.keys()) == {'source', 'followupEvent', 'contextOut'}
    assert response['followupEvent'] == {'data': {'preface': "I've left out the Qualified Privilege defence.",
                                                  'question': FD.extra_questions[2]},
                                         'name': 'trigger-bool'}
    assert response['contextOut'] == [{'lifespan': 20,
                                       'name': 'currentacc',
                                       'parameters': {'paragraphs': '6', 'defence': 'Fair Comment'}}]

    # AI: FD-extra-question-3?
    # me: skip
    c = controller.Controller(conversation, def_response)
    context = {'parameters': {
        'defence': 'Fair Comment',
        'question': FD.extra_questions[2]
    }}
    c.boolean_answer(context, False)
    c.save()
    response = c.get_response()
    del c
    del context
    assert set(response.keys()) == {'source', 'followupEvent', 'contextOut'}
    assert response['followupEvent'] == {'data': {'preface': "I've left out the Qualified Privilege defence.",
                                                  'question': FD.extra_questions[3]},
                                         'name': 'trigger-bool'}
    assert response['contextOut'] == [{'lifespan': 20,
                                       'name': 'currentacc',
                                       'parameters': {'paragraphs': '6', 'defence': 'Fair Comment'}}]

    # AI: FD-extra-question-4?
    # me: No
    c = controller.Controller(conversation, def_response)
    context = {'parameters': {
        'defence': 'Fair Comment',
        'question': FD.extra_questions[3]
    }}
    c.boolean_answer(context, False)
    c.save()
    response = c.get_response()
    del c
    del context
    assert set(response.keys()) == {'source', 'followupEvent', 'contextOut'}
    assert response['followupEvent'] == {'data': {'preface': "I've left out the Fair Comment defence."}, 'name': 'trigger-responsible'}
    assert response['contextOut'] == [{'lifespan': 20,
                                       'name': 'currentacc',
                                       'parameters': {'paragraphs': '6', 'defence': 'Responsible Communication'}}]

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
    assert response['followupEvent'] == {'data': {'preface': "I've left out the Fair Comment defence.",
                                                  'question': RD.extra_questions[0]},
                                         'name': 'trigger-bool'}
    assert response['contextOut'] == [{'lifespan': 20,
                                       'name': 'currentacc',
                                       'parameters': {'paragraphs': '6', 'defence': 'Responsible Communication'}}]

    # AI: There are a few questions to consider... Seriousness?
    # me: yes
    c = controller.Controller(conversation, def_response)
    context = {u'lifespan': 19,
              u'name': u'currentacc',
              u'parameters': {u'allegation': u'issue C',
                              u'answer': u'true',
                              u'answer.original': u'',
                              u'claim_id': float(claim_id3),
                              u'defence': u'Responsible Communication',
                              u'question': RD.extra_questions[0],
                              u'question.original': u''}}
    answer = True
    c.boolean_answer(context, answer)
    c.save()
    response = c.get_response()
    del c
    del context
    del answer
    assert set(response.keys()) == {'source', 'contextOut', 'followupEvent'}
    assert response['followupEvent'] == {'data': {'preface': "I've left out the Fair Comment defence.",
                                                  'question': RD.extra_questions[1]},
                                         'name': 'trigger-bool'}
    assert response['contextOut'] == [{'lifespan': 20,
                                       'name': 'currentacc',
                                       'parameters': {'paragraphs': '6', 'defence': 'Responsible Communication'}}]

    # AI: There are a few questions to consider... Diligence?
    # me: no
    c = controller.Controller(conversation, def_response)
    context = {u'lifespan': 19,
              u'name': u'currentacc',
              u'parameters': {u'allegation': u'issue C',
                              u'answer': u'false',
                              u'answer.original': u'',
                              u'claim_id': float(claim_id3),
                              u'defence': u'Responsible Communication',
                              u'question': RD.extra_questions[1],
                              u'question.original': u''}}
    answer = False
    c.boolean_answer(context, answer)
    c.save()
    response = c.get_response()
    del c
    del context
    del answer
    assert set(response.keys()) == {'source', 'contextOut', 'followupEvent'}
    assert response['followupEvent'] == {'data': {'preface': "I've left out the Fair Comment defence.",
                                                  'question': RD.extra_questions[2]},
                                         'name': 'trigger-bool'}
    assert response['contextOut'] == [{'lifespan': 20,
                                       'name': 'currentacc',
                                       'parameters': {'paragraphs': '6', 'defence': 'Responsible Communication'}}]

    # AI: There are a few questions to consider... Urgency?
    # me: yes
    c = controller.Controller(conversation, def_response)
    context = {u'lifespan': 19,
              u'name': u'currentacc',
              u'parameters': {u'allegation': u'issue C',
                              u'answer': u'true',
                              u'answer.original': u'',
                              u'claim_id': float(claim_id3),
                              u'defence': u'Responsible Communication',
                              u'question': RD.extra_questions[2],
                              u'question.original': u''}}
    answer = True
    c.boolean_answer(context, answer)
    c.save()
    response = c.get_response()
    del c
    del context
    del answer
    assert set(response.keys()) == {'source', 'contextOut', 'followupEvent'}
    assert response['followupEvent'] == {'data': {'preface': "I've left out the Fair Comment defence.",
                                                  'question': RD.extra_questions[3]},
                                         'name': 'trigger-bool'}
    assert response['contextOut'] == [{'lifespan': 20,
                                       'name': 'currentacc',
                                       'parameters': {'paragraphs': '6', 'defence': 'Responsible Communication'}}]

    # AI: There are a few questions to consider... Reliabilty?
    # me: skip
    c = controller.Controller(conversation, def_response)
    context = {u'lifespan': 19,
              u'name': u'currentacc',
              u'parameters': {u'allegation': u'issue C',
                              u'answer': u'skip',
                              u'answer.original': u'',
                              u'claim_id': float(claim_id3),
                              u'defence': u'Responsible Communication',
                              u'question': RD.extra_questions[3],
                              u'question.original': u''}}
    answer = 'skip'
    c.boolean_answer(context, answer)
    c.save()
    response = c.get_response()
    del c
    del context
    del answer
    assert set(response.keys()) == {'source', 'contextOut', 'followupEvent'}
    assert response['followupEvent'] == {'data': {'preface': "I've left out the Fair Comment defence.",
                                                  'question': RD.extra_questions[4]},
                                         'name': 'trigger-bool'}
    assert response['contextOut'] == [{'lifespan': 20,
                                       'name': 'currentacc',
                                       'parameters': {'paragraphs': '6', 'defence': 'Responsible Communication'}}]

    # AI: There are a few questions to consider... Equality?
    # me: yes
    c = controller.Controller(conversation, def_response)
    context = {u'lifespan': 19,
              u'name': u'currentacc',
              u'parameters': {u'allegation': u'issue C',
                              u'answer': u'true',
                              u'answer.original': u'',
                              u'claim_id': float(claim_id3),
                              u'defence': u'Responsible Communication',
                              u'question': RD.extra_questions[4],
                              u'question.original': u''}}
    answer = True
    c.boolean_answer(context, answer)
    c.save()
    response = c.get_response()
    del c
    del context
    del answer
    assert set(response.keys()) == {'source', 'contextOut', 'followupEvent'}
    assert response['followupEvent'] == {'data': {'preface': "I've left out the Fair Comment defence.",
                                                  'question': RD.extra_questions[5]},
                                         'name': 'trigger-bool'}
    assert response['contextOut'] == [{'lifespan': 20,
                                       'name': 'currentacc',
                                       'parameters': {'paragraphs': '6', 'defence': 'Responsible Communication'}}]

    # AI: There are a few questions to consider... Necessity?
    # me: no
    c = controller.Controller(conversation, def_response)
    context = {u'lifespan': 19,
              u'name': u'currentacc',
              u'parameters': {u'allegation': u'issue C',
                              u'answer': u'false',
                              u'answer.original': u'',
                              u'claim_id': float(claim_id3),
                              u'defence': u'Responsible Communication',
                              u'question': RD.extra_questions[5],
                              u'question.original': u''}}
    answer = False
    c.boolean_answer(context, answer)
    c.save()
    response = c.get_response()
    del c
    del context
    del answer
    assert set(response.keys()) == {'source', 'contextOut', 'followupEvent'}
    assert response['followupEvent'] == {'data': {'preface': "I've left out the Fair Comment defence.",
                                                  'question': RD.extra_questions[6]},
                                         'name': 'trigger-bool'}
    assert response['contextOut'] == [{'lifespan': 20,
                                       'name': 'currentacc',
                                       'parameters': {'paragraphs': '6', 'defence': 'Responsible Communication'}}]

    # AI: There are a few questions to consider... Reporting?
    # me: skip
    c = controller.Controller(conversation, def_response)
    context = {u'lifespan': 19,
              u'name': u'currentacc',
              u'parameters': {u'allegation': u'issue C',
                              u'answer': u'skip',
                              u'answer.original': u'',
                              u'claim_id': float(claim_id3),
                              u'defence': u'Responsible Communication',
                              u'question': RD.extra_questions[6],
                              u'question.original': u''}}
    answer = 'skip'
    c.boolean_answer(context, answer)
    c.save()
    response = c.get_response()
    del c
    del context
    del answer
    assert set(response.keys()) == {'source', 'contextOut', 'followupEvent'}
    assert response['followupEvent'] == {'data': {'preface': "I've left out the Fair Comment defence."}, 'name': 'trigger-facts'}
    assert response['contextOut'] == [{'lifespan': 20,
                                       'name': 'currentacc',
                                       'parameters': {'paragraphs': '6', 'defence': 'Responsible Communication'}}]

    # AI: Any additional facts?
    # me: nope
    c = controller.Controller(conversation, def_response)
    c.done_facts({'parameters': {'paragraphs': '6', 'defence': 'Responsible Communication'}})
    c.save()
    response = c.get_response()
    del c
    assert set(response.keys()) == {'source', 'contextOut', 'followupEvent'}
    assert response['followupEvent'] == {'data': {'preface': "Great, I've attached the Responsible Communication defence to your statement."},
                                         'name': 'trigger-defamatory'}

    # AI: were your comments defamatory?
    # me: yes
    c = controller.Controller(conversation, def_response)
    c.set_defamatory(True)
    c.save()
    response = c.get_response()
    del c
    assert set(response.keys()) == {'source', 'contextOut', 'followupEvent'}
    assert response['followupEvent'] == {'data': {'preface': ' '},
                                         'name': 'trigger-damaging'}

    # AI: were they damaged by your comments?
    # me: no
    c = controller.Controller(conversation, def_response)
    c.set_damaging(False)
    c.save()
    response = c.get_response()
    del c
    assert set(response.keys()) == {'source', 'contextOut', 'followupEvent'}
    assert response['followupEvent'] == {'data': {'preface': ' '},
                                         'name': 'trigger-apology'}

    # AI: did you issue an apology? When? Where?
    # me: yes; yesterday; local newspaper
    c = controller.Controller(conversation, def_response)
    c.set_apology({'happened': True, 'date': '2017-09-22', 'method': 'local newspaper'})
    c.save()
    response = c.get_response()
    del c
    assert set(response.keys()) == {'source', 'contextOut', 'followupEvent'}
    assert response['followupEvent'] == {'data': {'preface': ' '},
                                         'name': 'trigger-antislapp'}

    # AI: Are you being sued in Ontario? Is there public interest?
    # me: yes; no
    c = controller.Controller(conversation, def_response)
    c.set_antislapp(True, False)
    c.save()
    response = c.get_response()
    del c
    assert set(response.keys()) == {'source', 'contextOut', 'followupEvent'}
    assert response['followupEvent'] == {'data': {'preface': ' '},
                                         'name': 'trigger-court'}

    # AI: what is the name of the court?
    # me: Appeals Court of Alberta
    c = controller.Controller(conversation, def_response)
    c.set_court_name('Appeals Court of Alberta')
    c.save()
    response = c.get_response()
    del c
    assert set(response.keys()) == {'source', 'followupEvent'}
    assert response['followupEvent'] == {'data': {'preface': ' '},
                                         'name': 'trigger-summary'}

    # AI: in summary...
    c = controller.Controller(conversation, def_response)
    c.report()
    c.save()
    response = c.get_response()
    del c
    assert set(response.keys()) == {'source', 'speech', 'displayText'}
    assert response['speech'] == response['displayText']
    assert response['speech'].count("Download") == 2

    c = controller.Controller(conversation, def_response)
    assert c.defence.sued == True
    assert c.defence.plaintiff == 'Bob'
    assert c.defence.defendant == 'Joe'

    assert c.defence.get_claims() == [
        {'allegation': 'issue A', 'paragraph': 9, 'plead': u'agree'},
        {'allegation': 'issue B', 'paragraph': '4, 5', 'plead': u'withhold'},
        {'allegation': 'issue C', 'paragraph': 6, 'plead': u'deny'}
    ]

    assert [claim['paragraph'] for claim in c.defence.get_withheld()] == ['4, 5']
    assert [claim['paragraph'] for claim in c.defence.get_agreed()] == [9]
    assert [claim['paragraph'] for claim in c.defence.get_denied()] == [6]
    defences = c.defence.get_defences()
    assert set(defences.keys()) == {'Truth', 'Absolute Privilege', 'Qualified Privilege', 'Fair Comment', 'Responsible Communication'}

    assert c.defence.defamatory is True
    assert c.defence.damaging is False
    assert c.defence.get_apology() == (True, 'September 22, 2017', 'local newspaper')
    assert c.defence.antislapp is False
    assert c.defence.court_name == 'Appeals Court of Alberta'
