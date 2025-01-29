from json import JSONDecodeError

import requests
import json
from rest_framework import response


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
        try:
            resp = requests.post(self.url, headers=self.headers, json=payload, verify=False)
            resp = resp.json()
            resp = resp.get("choices")[0].get("message").get("content")
            resp = resp.replace('```json\n', '').replace('```', '').replace('\n', '').replace('    ', '')
            resp = json.loads(resp)
        except JSONDecodeError:
            resp = response.Response(data={"error": "Invalid response from Perplexity API"}, status=500)
        except TypeError:
            resp = response.Response(data={"error": "Invalid response from Perplexity API"}, status=500)

        return resp