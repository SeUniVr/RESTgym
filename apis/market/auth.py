import requests
import json

class Authenticate:

    token = None

    def get_token(self):
        signup_url = 'http://localhost:8080/register'
        signup_payload = json.dumps({
            'email': 'anothertestuser@gmail.com',
            'password': 'testing',
            'phone':'+39 3406089282',
            'address':'address',
            'name':'test'
        })
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        signup_response = requests.request('POST', signup_url, headers=headers, data=signup_payload)
        self.token = str(signup_response.cookies.get_dict()['JSESSIONID'])
        print(f'Token retrieved: {self.token}')

    def request(self, flow):
        if self.token == None:
            self.get_token()
        flow.request.headers['Cookie'] = 'JSESSIONID=' + self.token

addons = [Authenticate()]