import json

from utils.cowin_sdk import CowinAPI
from utils.utils import response_handler

def get_states(event, context):
    cowin = CowinAPI()
    states = cowin.get_states()
    return response_handler(states, 200)

def get_districts(event, context):
    cowin = CowinAPI()
    state_id = event["queryStringParameters"]["state_id"]
    districts = cowin.get_districts(state_id)
    return response_handler(districts, 200)

def get_centers(event, context):
    cowin = CowinAPI()
    district_id = event["queryStringParameters"]["district_id"]
    date = event["queryStringParameters"]["date"]
    centers = cowin.get_centers(district_id, date)
    return response_handler(centers, 200)