import time

import requests

TRIGGER_URL = 'https://a7nn6pz85i.execute-api.ap-south-1.amazonaws.com/dev/trigger'

if __name__ == "__main__":
    while True:
        response = requests.post(TRIGGER_URL)
        time.sleep(20)