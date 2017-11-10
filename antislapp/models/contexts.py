import apiai
import requests
from antislapp import index
import httplib


class Contexts():
    def __init__(self, session_id):
        self.base_url = "https://api.dialogflow.com/v1"
        self.endpoint = "/contexts"
        self.session_id = session_id
        self.token = index.CLIENT_ACCESS_TOKEN

    def get(self):
        # context_model = apiai.Request(self.token, self.base_url, self.endpoint, ["sessionId={}".format(self.session_id)])

        #url = "{}{}?v=20150910&sessionId={}".format(self.base_url, self.endpoint, self.session_id)
        url = "{}{}?v=20150910&sessionId={}".format(self.base_url, self.endpoint, self.session_id)
        headers = {
            'content-type': 'application/json',
            'authorization': 'bearer {}'.format(self.token)
        }
        print("trying url: {}".format(url))
        response = requests.get(url, headers=headers)

        return response

    def set(self):
        pass