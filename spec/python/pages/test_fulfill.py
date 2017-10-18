from antislapp.pages import fulfill


sample_data1 = '{"id":"9975da59-64fb-4c65-a4e8-e98e55ee9a82","timestamp":"2017-10-04T17:57:43.466Z","lang":"en","result":{"source":"agent","resolvedQuery":"weather for today","speech":"","action":"","actionIncomplete":false,"parameters":{"date":"2017-10-04","geo-city":""},"contexts":[],"metadata":{"intentId":"5fcddff3-761b-47d8-a551-acf6bbbfb7ac","webhookUsed":"true","webhookForSlotFillingUsed":"false","intentName":"Weather"},"fulfillment":{"speech":"I\\u0027m not sure about the weather on 2017-10-04","messages":[{"type":0,"id":"1222c926-dc5d-4d10-9635-8cf5ea305c30","speech":"I\\u0027m not sure about the weather on 2017-10-04"}]},"score":1.0},"status":{"code":200,"errorType":"success"},"sessionId":"a00ab1e4-269e-4a3a-bf67-702877dfbb1c"}'
# data1 = json.loads(sample_data)
data1 = {
    u'id': u'9975da59-64fb-4c65-a4e8-e98e55ee9a82',
    u'lang': u'en',
    u'result': {
        u'action': u'',
        u'actionIncomplete': False,
        u'contexts': [],
        u'fulfillment': {
            u'messages': [
                {u'id': u'1222c926-dc5d-4d10-9635-8cf5ea305c30',
                u'speech': u"I'm not sure about the weather on 2017-10-04",
                u'type': 0}
            ],
            u'speech': u"I'm not sure about the weather on 2017-10-04"},
        u'metadata': {
            u'intentId': u'5fcddff3-761b-47d8-a551-acf6bbbfb7ac',
            u'intentName': u'Weather',
            u'webhookForSlotFillingUsed': u'false',
            u'webhookUsed': u'true'},
        u'parameters': {
            u'date': u'2017-10-04',
            u'geo-city': u''},
        u'resolvedQuery': u'weather for today',
        u'score': 1.0,
        u'source': u'agent',
        u'speech': u''},
    u'sessionId': u'a00ab1e4-269e-4a3a-bf67-702877dfbb1c',
    u'status': {u'code': 200, u'errorType': u'success'},
    u'timestamp': u'2017-10-04T17:57:43.466Z'}


# multi-part conversation, gathering all required items. Only the last message, once all required parameters are filled, is submitted for fulfillment.
sample_data2 = '{"id":"848e2b19-6a44-4df8-9328-e1d5aeba5b24","timestamp":"2017-10-04T19:34:20.19Z","lang":"en","result":{"source":"agent","resolvedQuery":"Austin","speech":"","action":"","actionIncomplete":false,"parameters":{"date":"2017-10-05","geo-city":"Austin"},"contexts":[],"metadata":{"intentId":"5fcddff3-761b-47d8-a551-acf6bbbfb7ac","webhookUsed":"true","webhookForSlotFillingUsed":"false","intentName":"Weather"},"fulfillment":{"speech":"I don\\u0027t know the weather for 2017-10-05 in Austin","messages":[{"type":0,"id":"130e561f-b206-4cea-b03c-42a2ebf45ea4","speech":"I don\\u0027t know the weather for 2017-10-05 in Austin"}]},"score":1.0},"status":{"code":200,"errorType":"success"},"sessionId":"a00ab1e4-269e-4a3a-bf67-702877dfbb1c"}'
data2 = {
    u'id': u'848e2b19-6a44-4df8-9328-e1d5aeba5b24',
    u'lang': u'en',
    u'result': {
        u'action': u'bogus',
        u'actionIncomplete': False,
        u'contexts': [],
        u'fulfillment': {
            u'messages': [
                {u'id': u'130e561f-b206-4cea-b03c-42a2ebf45ea4',
                u'speech': u"I don't know the weather for 2017-10-05 in Austin",
                u'type': 0}
            ],
            u'speech': u"I don't know the weather for 2017-10-05 in Austin"},
        u'metadata': {
            u'intentId': u'5fcddff3-761b-47d8-a551-acf6bbbfb7ac',
            u'intentName': u'Weather',
            u'webhookForSlotFillingUsed': u'false',
            u'webhookUsed': u'true'},
        u'parameters': {
            u'date': u'2017-10-05',
            u'geo-city': u'Austin'},
        u'resolvedQuery': u'Austin',
        u'score': 1.0,
        u'source': u'agent',
        u'speech': u''},
    u'sessionId': u'a00ab1e4-269e-4a3a-bf67-702877dfbb1c',
    u'status': {u'code': 200, u'errorType': u'success'},
    u'timestamp': u'2017-10-04T19:34:20.19Z'}


# "what's the weather in paris today?"
sample_data3 = '{"id":"443f92e4-547a-4fa6-b045-2680e0db487d","timestamp":"2017-10-04T22:14:46.033Z","lang":"en","result":{"source":"agent","resolvedQuery":"What\\u0027s the weather in paris today","speech":"","action":"","actionIncomplete":false,"parameters":{"date":"2017-10-04","geo-city":"Paris"},"contexts":[{"name":"location","parameters":{"date":"2017-10-04","geo-city":"Paris","date.original":"today","geo-city.original":"paris"},"lifespan":5}],"metadata":{"intentId":"5fcddff3-761b-47d8-a551-acf6bbbfb7ac","webhookUsed":"true","webhookForSlotFillingUsed":"false","intentName":"Weather"},"fulfillment":{"speech":"I don\\u0027t know the weather for 2017-10-04 in Paris","messages":[{"type":0,"id":"3e4b57d1-312e-4c23-add2-7fc43d9b2c98","speech":"I don\\u0027t know the weather for 2017-10-04 in Paris"}]},"score":0.9200000166893005},"status":{"code":200,"errorType":"success"},"sessionId":"c15a6d3a-305c-3f00-af2c-3282aef39aa3"}'
data3 = {
    u'id': u'443f92e4-547a-4fa6-b045-2680e0db487d',
    u'lang': u'en',
    u'result': {
        u'action': u'checking',
        u'actionIncomplete': False,
        u'contexts': [
            {u'lifespan': 5,
            u'name': u'location',
            u'parameters': {
                u'date': u'2017-10-04',
                u'date.original': u'today',
                u'geo-city': u'Paris',
                u'geo-city.original': u'paris'}}
        ],
        u'fulfillment': {
            u'messages': [
                {u'id': u'3e4b57d1-312e-4c23-add2-7fc43d9b2c98',
                u'speech': u"I don't know the weather for 2017-10-04 in Paris",
                u'type': 0}
            ],
            u'speech': u"I don't know the weather for 2017-10-04 in Paris"},
        u'metadata': {
            u'intentId': u'5fcddff3-761b-47d8-a551-acf6bbbfb7ac',
            u'intentName': u'Weather',
            u'webhookForSlotFillingUsed': u'false',
            u'webhookUsed': u'true'},
        u'parameters': {
            u'date': u'2017-10-04',
            u'geo-city': u'Paris'},
        u'resolvedQuery': u"What's the weather in paris today",
        u'score': 0.9200000166893005,
        u'source': u'agent',
        u'speech': u''},
    u'sessionId': u'c15a6d3a-305c-3f00-af2c-3282aef39aa3',
    u'status': {u'code': 200, u'errorType': u'success'},
    u'timestamp': u'2017-10-04T22:14:46.033Z'}

# "how about tomorrow?" (keeping context from paris question above)
sample_data4 = '{"id":"efc62e61-e249-4fb6-a508-a60da5851aad","timestamp":"2017-10-04T22:15:28.531Z","lang":"en","result":{"source":"agent","resolvedQuery":"how about tomorrow?","speech":"","action":"","actionIncomplete":false,"parameters":{"date":"2017-10-05","date-period":"","geo-city":"Paris"},"contexts":[{"name":"location","parameters":{"date":"2017-10-05","geo-city":"Paris","date.original":"tomorrow","date-period.original":"","geo-city.original":"","date-period":""},"lifespan":5}],"metadata":{"intentId":"9f2a2ac0-f49b-4a40-8a6c-c4f167cf97ba","webhookUsed":"true","webhookForSlotFillingUsed":"false","intentName":"weather.context"},"fulfillment":{"speech":"","messages":[{"type":0,"id":"407bd516-f436-48a7-8283-9c89ed9e5d96","speech":""}]},"score":0.5699999928474426},"status":{"code":200,"errorType":"success"},"sessionId":"c15a6d3a-305c-3f00-af2c-3282aef39aa3"}'
data4 = {
    u'id': u'efc62e61-e249-4fb6-a508-a60da5851aad',
    u'lang': u'en',
    u'result': {
        u'action': u'',
        u'actionIncomplete': False,
        u'contexts': [
            {u'lifespan': 5,
            u'name': u'location',
            u'parameters': {
                u'date': u'2017-10-05',
                u'date-period': u'',
                u'date-period.original': u'',
                u'date.original': u'tomorrow',
                u'geo-city': u'Paris',
                u'geo-city.original': u''}}
        ],
        u'fulfillment': {
            u'messages': [
                {u'id': u'407bd516-f436-48a7-8283-9c89ed9e5d96',
                u'speech': u'',
                u'type': 0}],
            u'speech': u''},
        u'metadata': {
            u'intentId': u'9f2a2ac0-f49b-4a40-8a6c-c4f167cf97ba',
            u'intentName': u'weather.context',
            u'webhookForSlotFillingUsed': u'false',
            u'webhookUsed': u'true'},
        u'parameters': {
            u'date': u'2017-10-05',
            u'date-period': u'',
            u'geo-city': u'Paris'},
        u'resolvedQuery': u'how about tomorrow?',
        u'score': 0.5699999928474426,
        u'source': u'agent',
        u'speech': u''},
    u'sessionId': u'c15a6d3a-305c-3f00-af2c-3282aef39aa3',
    u'status': {u'code': 200, u'errorType': u'success'},
    u'timestamp': u'2017-10-04T22:15:28.531Z'}


def test_extract():
    ex = fulfill.Fulfill.extract_parameters

    assert ex(data1) == {u'date': u'2017-10-04', u'geo-city': u''}
    assert ex(data2) == {u'date': u'2017-10-05', u'geo-city': u'Austin'}
    assert ex(data3) == {u'date': u'2017-10-04', u'geo-city': u'Paris'}
    assert ex(data4) == {u'date': u'2017-10-05', u'date-period': u'', u'geo-city': u'Paris'}


def test_def_response():
    ex = fulfill.Fulfill.extract_default_response

    assert ex(data1) == u"I'm not sure about the weather on 2017-10-04"
    assert ex(data2) == u"I don't know the weather for 2017-10-05 in Austin"
    assert ex(data3) == u"I don't know the weather for 2017-10-04 in Paris"
    assert ex(data4) == u''


def test_extract_action():
    ex = fulfill.Fulfill.extract_action
    assert ex(data1) == u''
    assert ex(data2) == u'bogus'
    assert ex(data3) == u'checking'
    assert ex(data4) == u''


def test_join_list():
    ex = fulfill.Fulfill.join_list
    assert ex([]) == ''
    assert ex(['a']) == 'a'
    assert ex(['a', 'b']) == 'a and b'
    assert ex(['a', 'b', 'c']) == 'a, b, and c'
    assert ex(['a', 'b', 'c', 'd']) == 'a, b, c, and d'


def test_extract_contexts():
    ex = fulfill.Fulfill.extract_contexts

    assert ex(data1) == {}
    assert ex(data2) == {}
    assert ex(data3) == {
        u'location': {
            u'lifespan': 5,
            u'date': u'2017-10-04',
            u'date.original': u'today',
            u'geo-city': u'Paris',
            u'geo-city.original': u'paris'}
    }
    assert ex(data4) == {
        u'location': {
            u'lifespan': 5,
            u'date': u'2017-10-05',
            u'date-period': u'',
            u'date-period.original': u'',
            u'date.original': u'tomorrow',
            u'geo-city': u'Paris',
            u'geo-city.original': u''}
    }


def test_summarize():
    ex = fulfill.Fulfill.summarize
    params = {}
    assert ex(params) == "So, to summarize: you have not been sued and your words were untrue"

    params = {'sued': True, 'truth': True, 'truth-evidence': False, 'absolute': False, 'qualified': True}
    assert ex(params) == "So, to summarize: you have been sued, " \
                         "your words were true but you have no proof, " \
                         "you weren't in a position of absolute privilege, " \
                         "and you were in a position of qualified privilege"
