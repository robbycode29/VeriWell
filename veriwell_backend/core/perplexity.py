import requests
import json


class Perplexity:
    """
    Perplexity class to interact with the Perplexity API
    """
    def __init__(self, key):
        self.url = "https://api.perplexity.ai/chat/completions"
        self.API_KEY = key
        self.headers = {"Authorization": f"Bearer {self.API_KEY}"}

    def ask(self, payload):
        """
        Ask a question to the Perplexity API
        """
        response = requests.post(self.url, headers=self.headers, json=payload, verify=False)
        response = response.json()
        response = response.get("choices")[0].get("message").get("content")
        response = response.replace('```json\n', '').replace('```', '').replace('\n', '').replace('    ', '')
        response = json.loads(response)

        return response