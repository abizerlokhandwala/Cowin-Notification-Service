import logging
import random
from datetime import date, timedelta

import requests

from helpers.constants import STATES_URL, DISTRICTS_URL, CALENDAR_BY_DISTRICT_URL, FIND_BY_DISTRICT_URL

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class CowinAPI:

    def __init__(self):
        self.user_agent_list = open('./helpers/ua.txt').read().splitlines()
        pass

    def get_states(self):
        headers = {
            'User-Agent': random.choice(self.user_agent_list)
        }
        response = requests.get(STATES_URL, headers=headers)
        response = response.json()
        return response['states']

    def get_districts(self, state_id):
        headers = {
            'User-Agent': random.choice(self.user_agent_list)
        }
        response = requests.get(f'{DISTRICTS_URL}{state_id}', headers=headers)
        response = response.json()
        return response['districts']

    def get_centers_7(self, district_id, date_val):
        headers = {
            'User-Agent': random.choice(self.user_agent_list)
        }
        response = requests.get(f'{CALENDAR_BY_DISTRICT_URL}?district_id={district_id}&date={date_val}', headers=headers)
        logger.info(f'Status: {response.status_code}')
        if response.status_code >= 400:
            response = {
                'centers':[]
            }
        else:
            response = response.json()
        centers = response['centers']
        return centers

    def get_centers_7_old(self, district_id, date_val):
        headers = {
            'User-Agent': random.choice(self.user_agent_list)
        }
        response = requests.get(f'{FIND_BY_DISTRICT_URL}?district_id={district_id}&date={date_val}', headers=headers)
        logger.info(f'Status: {response.status_code}')
        if response.status_code >= 400:
            response = {
                'sessions':[]
            }
        else:
            response = response.json()
        centers = response['sessions']
        date_tomorrow = (date.today() + timedelta(days=1)).strftime("%d-%m-%Y")
        headers = {
            'User-Agent': random.choice(self.user_agent_list)
        }
        response = requests.get(f'{FIND_BY_DISTRICT_URL}?district_id={district_id}&date={date_tomorrow}', headers=headers)
        if response.status_code >= 400:
            response = {
                'sessions': []
            }
        else:
            response = response.json()
        centers+=response['sessions']
        return centers