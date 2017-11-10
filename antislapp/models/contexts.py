import apiai
import requests
from antislapp import index
import httplib


class Contexts():
    def __init__(self, session_id):
        self.base_url = "https://api.dialogflow.com/v1"
        self.endpoint = "/contexts"
        self.session_id = session_id[:36]
        self.token = index.CLIENT_ACCESS_TOKEN

    def get(self):
        url = "{}{}?sessionId={}".format(self.base_url, self.endpoint, self.session_id)
        headers = {
            'content-type': 'application/json',
            'authorization': 'bearer {}'.format(self.token)
        }
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            raise KeyError(response.content)

        return response.content

    def set(self, contexts):
        url = "{}{}?sessionId={}".format(self.base_url, self.endpoint, self.session_id)
        headers = {
            'content-type': 'application/json',
            'authorization': 'bearer {}'.format(self.token)
        }
        response = requests.post(url, contexts, headers=headers)
        if response.status_code != 200:
            raise KeyError(response.content)

        return response.content