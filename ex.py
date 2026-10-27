import requests
import json

class WolframAlphaClient:
    def __init__(self, app_id):
        self.base_url = "http://api.wolframalpha.com/v2/query"
        self.app_id = app_id
    
    def query(self, input_text):
        params = {
            'input': input_text,
            'format': 'plaintext',
            'output': 'json',
            'appid': self.app_id
        }
        response = requests.get(self.base_url, params=params)
        return response.json()

if __name__ == "__main__":
    client = WolframAlphaClient("8AW4X7UEW8")
    result = client.query("population of Russia")
    print(json.dumps(result, indent=2))
