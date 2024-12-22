import requests
import json

class Authenticate:

    token = None

    def get_token(self):
        signup_url = "http://localhost:8080/api/auth/signup"
        signin_url = "http://localhost:8080/api/auth/signin"
        signup_payload = json.dumps({
            "firstName": "userFirstName",
            "lastName": "userLastName",
            "username": "userUsername",
            "password": "userPassword",
            "email": "user@gmail.com"
        })
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        signup_response = requests.request("POST", signup_url, headers=headers, data=signup_payload)
        signin_payload = json.dumps({
            "usernameOrEmail": "userUsername",
            "password": "userPassword"
        })
        signin_response = requests.request("POST", signin_url, headers=headers, data=signin_payload)
        self.token = str(signin_response.json()['accessToken'])
        print(f"Token retrieved: {self.token}")

    def request(self, flow):
        if self.token == None:
            self.get_token()
        flow.request.headers["Authorization"] = "Bearer " + self.token

addons = [Authenticate()]