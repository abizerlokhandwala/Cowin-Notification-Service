import logging
import os

import requests

from helpers.constants import STATES_URL, DISTRICTS_URL, CALENDAR_BY_DISTRICT_URL

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class CowinAPI:

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36',
            'Authorization': f'Bearer {os.getenv("AUTH_TOKEN")}'
        }
        pass

    def get_states(self):
        response = requests.get(STATES_URL, headers=self.headers)
        response = response.json()
        return response['states']

    def get_districts(self, state_id):
        response = requests.get(f'{DISTRICTS_URL}{state_id}', headers=self.headers)
        response = response.json()
        return response['districts']

    def get_centers_7(self, district_id, date):
        response = requests.get(f'{CALENDAR_BY_DISTRICT_URL}?district_id={district_id}&date={date}', headers=self.headers)
        response = response.json()
        return response['centers']
