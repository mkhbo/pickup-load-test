import json
import sys
import os
from pprint import pformat, pprint
import requests

class TokenGenerator():
    US_PAYLOAD_TEMPLATE_PATH = 'token_payloads/us.json'
    TOKEN_TOOL_URI = 'https://tokens.staging.hurley.hbo.com/devTools/buildTokenForAutomatedTest/'
    
    def __init__(self):
        self.cache = {}
        self.us_payload_template = self.load_payload_template()
        
    def load_payload_template(self):
        script_dir = os.path.dirname(__file__)
        file_path = os.path.join(script_dir, self.US_PAYLOAD_TEMPLATE_PATH)
        with open(file_path, 'r') as file:
            data = file.read()
            return json.loads(data)
    
    def get_token(self, user):
        if user in self.cache:
            return self.cache[user]
        token = self.request_token(user)
        if not token:
            return None
        self.cache[user]=token
        return token
    
    def request_token(self,user):
        payload = self.us_payload_template
        additionalTokenPropertyData = payload['testParameters']['additionalTokenPropertyData']
        additionalTokenPropertyData["userId"]=additionalTokenPropertyData["hurleyAccountId"]=additionalTokenPropertyData["hurleyProfileId"]=additionalTokenPropertyData["streamTrackingId"]=user
        response=None
        response = requests.post(self.TOKEN_TOOL_URI, json=payload)
        if response.status_code!=200:
            raise Exception('HTTP Request returned status code {0}'.format(response.status_code))
        try:
            response_payload=response.json()
            return response_payload['encryptedToken']
        except:
            raise Exception('could not find token in the response sent by hurley tokens service, missing key "encryptedToken"')
