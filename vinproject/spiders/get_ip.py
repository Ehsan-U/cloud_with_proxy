import requests
import json

def get():
    response = requests.get('http://httpbin.org/ip').content
    dict = json.loads(response)
    return dict.get('origin')
