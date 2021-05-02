import requests

from helpers.constants import STATES_URL, DISTRICTS_URL, CALENDAR_BY_DISTRICT_URL


class CowinAPI:

    def __init__(self):
        pass

    def get_states(self):
        response = requests.get(STATES_URL)
        response = response.json()
        return response['states']

    def get_districts(self, state_id):
        response = requests.get(f'{DISTRICTS_URL}{state_id}')
        response = response.json()
        return response['districts']

    def get_centers_7(self, district_id, date):
        response = requests.get(f'{CALENDAR_BY_DISTRICT_URL}?district_id={district_id}&date={date}')
        response = response.json()
        return response['centers']
