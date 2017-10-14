import requests
import json

data = {u'id': u'ef893476-ef9b-4e6e-9cac-2f343881f3fe',
 u'lang': u'en',
 u'result': {u'action': u'd-fc',
             u'actionIncomplete': False,
             u'contexts': [{u'lifespan': 5,
                            u'name': u'defense',
                            u'parameters': {u'absolute': u'false',
                                            u'absolute.original': u'',
                                            u'abspriv': u'false',
                                            u'abspriv.original': u'',
                                            u'comment': u'true',
                                            u'comment.original': u'',
                                            u'qualified': u'false',
                                            u'qualified.original': u'',
                                            u'sued': u'true',
                                            u'sued.original': u'',
                                            u'truth': u'true',
                                            u'truth-evidence': u'false',
                                            u'truth-evidence.original': u'',
                                            u'truth.original': u''}}],
             u'fulfillment': {u'messages': [{u'id': u'f43266f6-b0b1-487a-8610-9fcf8a7a7ad9',
                                             u'speech': u'Great! I would advise the use of "Fair Comment" as your defense.',
                                             u'type': 0}],
                              u'speech': u'Great! I would advise the use of "Fair Comment" as your defense.'},
             u'metadata': {u'intentId': u'279e6e59-ae09-4d5d-8360-04f2ac00c312',
                           u'intentName': u'5comment-yes-7defense',
                           u'webhookForSlotFillingUsed': u'false',
                           u'webhookUsed': u'true'},
             u'parameters': {u'absolute': u'false',
                             u'abspriv': u'false',
                             u'comment': u'true',
                             u'qualified': u'false',
                             u'sued': u'true',
                             u'truth': u'true',
                             u'truth-evidence': u'false'},
             u'resolvedQuery': u'yes',
             u'score': 1.0,
             u'source': u'agent',
             u'speech': u''},
 u'sessionId': u'7ec0b66f-00d2-4236-951e-da042ee7aace',
 u'status': {u'code': 200, u'errorType': u'success'},
 u'timestamp': u'2017-10-13T22:34:45.869Z'}
sample_data = json.dumps(data)


def test_post():
    #url = "http://riobot.centralus.cloudapp.azure.com/fulfill"
    url = "http://localhost:8080/fulfill"
    response = requests.post(url, data=sample_data)
    assert response.status_code == 200
    from pprint import pprint
    decoded = json.loads(response.content)
    assert decoded.get("speech", '') == 'So, to summarize: you have been sued, your words were true but you have ' \
                                        'no proof, you weren\'t in a position of absolute privilege, you weren\'t ' \
                                        'in a position of qualified privilege, and you were expressing your opinion ' \
                                        'on a matter of public interest. Great! I would advise the use ' \
                                        'of "Fair Comment" as your defense.'
