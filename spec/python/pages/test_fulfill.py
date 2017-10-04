from antislapp.pages import fulfill


sample_data = '{"id":"9975da59-64fb-4c65-a4e8-e98e55ee9a82","timestamp":"2017-10-04T17:57:43.466Z","lang":"en","result":{"source":"agent","resolvedQuery":"weather for today","speech":"","action":"","actionIncomplete":false,"parameters":{"date":"2017-10-04","geo-city":""},"contexts":[],"metadata":{"intentId":"5fcddff3-761b-47d8-a551-acf6bbbfb7ac","webhookUsed":"true","webhookForSlotFillingUsed":"false","intentName":"Weather"},"fulfillment":{"speech":"I\\u0027m not sure about the weather on 2017-10-04","messages":[{"type":0,"id":"1222c926-dc5d-4d10-9635-8cf5ea305c30","speech":"I\\u0027m not sure about the weather on 2017-10-04"}]},"score":1.0},"status":{"code":200,"errorType":"success"},"sessionId":"a00ab1e4-269e-4a3a-bf67-702877dfbb1c"}'
# data = json.loads(sample_data)
data = {
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
