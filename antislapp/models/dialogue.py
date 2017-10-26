import os
import web
import json
import apiai
import base64
import random
from antislapp import index


CLIENT_ACCESS_TOKEN = os.environ.get('CLIENT_ACCESS_TOKEN', 'YOUR_ACCESS_TOKEN')


class Response:
    """
    { "id": "ba29de8e-3288-4157-ab9d-db5a1fd7ed68",
      "timestamp": "2017-10-26T18:01:32.823Z",
      "lang": "en",
      "result": {
        "source": "agent",
        "resolvedQuery": "define man",
        "action": "is_sued",
        "actionIncomplete": false,
        "parameters": {
          "sued": "true"
        },
        "contexts": [
          {
            "name": "getting_accusations",
            "parameters": {
              "sued": "true",
              "sued.original": ""
            },
            "lifespan": 5
          },
          {
            "name": "defaultwelcomeintent-followup",
            "parameters": {
              "sued": "true",
              "sued.original": ""
            },
            "lifespan": 1
          }
        ],
        "metadata": {
          "intentId": "e409f66b-4952-4665-a7fe-d16875093845",
          "webhookUsed": "true",
          "webhookForSlotFillingUsed": "false",
          "webhookResponseTime": 623,
          "intentName": "Default Welcome Intent - yes"
        },
        "fulfillment": {
          "speech": "There are a few ways to respond to a suit, ...",
          "source": "riobot",
          "displayText": "There are a few ways to respond to a suit, ...",
          "messages": [
            {
              "type": 0,
              "id": "c8319608-9fd4-461a-8064-ed32e951941b",
              "speech": "There are a few ways to respond to a suit, ..."
            }
          ]
        },
        "score": 0.41999998688697815
      },
      "alternateResult": {
        "source": "domains",
        "resolvedQuery": "define man",
        "actionIncomplete": false,
        "contexts": [],
        "metadata": {},
        "fulfillment": {
          "speech": "",
          "source": "deepLearning"
        },
        "score": 0.0
      },
      "status": {
        "code": 200,
        "errorType": "success"
      },
      "sessionId": "MC40NzA1NjUyNDM1ODAuNDIxODUxMz"
    }
    """
    def __init__(self, response):
        self.raw = response.read()
        self.data = json.loads(self.raw)
        self.result = self.data.get("result", {})
        self.fulfillment = self.result.get("fulfillment", {})

    def get_speech(self):
        return self.fulfillment.get("speech", "Error getting speech")

    def get_data(self):
        return self.fulfillment.get("data", {})


class Dialogue:
    def __init__(self, session, db):
        """
        :type session: str
        :type db: web.DB
        """
        self.session = session
        self.db = db
        self.ai = apiai.ApiAI(CLIENT_ACCESS_TOKEN)
        self.lang = 'en'

    def send_message(self, msg):
        request = self.ai.text_request()
        request.lang = self.lang
        request.session_id = self.session
        request.query = msg
        response = Response(request.getresponse())
        # TODO: save any parts of response desired. (e.g. message history. data. params.)
        return response



class Interactive():
    def __init__(self):
        self.session = base64.encodestring(str(random.random())+str(random.random()))[:30]
        self.dialogue = Dialogue(self.session, index.db)

    def start(self):
        response = None
        while True:
            msg = raw_input(">")
            if msg == 'exit':
                break
            elif msg == '_' and response:
                print(response.raw)
            response = self.dialogue.send_message(msg)
            print(response.get_speech())