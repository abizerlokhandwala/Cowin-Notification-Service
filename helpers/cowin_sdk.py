import logging
import random
import string
from datetime import date, timedelta

import aiohttp
import requests

from helpers.constants import STATES_URL, DISTRICTS_URL, FIND_BY_DISTRICT_URL, CALENDAR_BY_DISTRICT_PUBLIC_URL

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class CowinAPI:

    def __init__(self):
        self.user_agent_list = open('./helpers/ua.txt').read().splitlines()
        self.len = 30
        pass

    def random_str(self):
        res = ''.join(random.choices(string.ascii_uppercase + string.digits, k=self.len))
        return str(res)

    def get_states(self):
        headers = {
            'User-Agent': self.random_str()
        }
        response = requests.get(STATES_URL, headers=headers)
        response = response.json()
        return response['states']

    def get_districts(self, state_id):
        headers = {
            'User-Agent': self.random_str()
        }
        response = requests.get(f'{DISTRICTS_URL}{state_id}', headers=headers)
        response = response.json()
        return response['districts']

    def get_centers_7(self, district_id, date_val):
        headers = {
            'User-Agent': self.random_str()
        }
        response = requests.get(f'{CALENDAR_BY_DISTRICT_PUBLIC_URL}?district_id={district_id}&date={date_val}',
                                headers=headers)
        logger.info(f'Status: {response.status_code}')
        if response.status_code >= 400:
            response = {
                'centers': []
            }
        else:
            response = response.json()
        centers = response['centers']
        return centers

    async def get_centers_7_old(self, district_id, date_val):
        headers = {
            'User-Agent': self.random_str()
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(f'{FIND_BY_DISTRICT_URL}?district_id={district_id}&date={date_val}',
                                   headers=headers) as response:
                logger.info(f'Status: {response.status}')
                if response.status >= 400:
                    response = {
                        'sessions': []
                    }
                else:
                    response = await response.json()
        centers = response['sessions']
        date_tomorrow = (date.today() + timedelta(days=1)).strftime("%d-%m-%Y")
        headers = {
            'User-Agent': self.random_str()
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(f'{FIND_BY_DISTRICT_URL}?district_id={district_id}&date={date_tomorrow}',
                                   headers=headers) as response:
                if response.status >= 400:
                    response = {
                        'sessions': []
                    }
                else:
                    response = await response.json()
        centers += response['sessions']
        return centers
