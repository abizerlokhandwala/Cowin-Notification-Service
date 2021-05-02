import json

from helpers.constants import ISSUE_MSG
from helpers.cowin_sdk import CowinAPI
from helpers.db_handler import DBHandler
from helpers.email_handler import EmailHandler
from helpers.utils import response_handler, get_preference_slots


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
    centers = cowin.get_centers_7(district_id, date)
    return response_handler(centers, 200)

def get_district_preferences(event, context):
    district_id = event["queryStringParameters"]['district_id']
    vaccine = event["queryStringParameters"]['vaccine']
    age_group = event["queryStringParameters"]['age_group']
    return response_handler(get_preference_slots(district_id, vaccine, age_group),200)

def subscribe(event, context):
    body = json.loads(event['body'])
    # body = {
    #     "email":"abizerl123@gmail.com",
    #     "phone_number": "123",
    #     "subscriptions": [{"vaccine":"abcd","age_group": "abcd","district_id":"123"}, {"vaccine":"abc","age_group": "abcd","district_id":"123"}]
    # }
    db = DBHandler.get_instance()
    email = EmailHandler.get_instance()
    is_verified, verification_token = db.subscribe(body)
    if is_verified == -1:
        return response_handler({'message': f'Email Already exists'}, 400)
    additional_comments = ''
    # if is_verified is False:
    #     email.sendVerificationEmail(body['email'])
    #     additional_comments = f'Please verify your email ID: {body["email"]}'
    return response_handler({'message': f'Subscribed successfully! {additional_comments}'}, 201)

def unsubscribe(event, context):
    sub_id = event["queryStringParameters"]["subscription_id"]
    user_email = event["queryStringParameters"]["email"]
    db = DBHandler.get_instance()
    if db.unsubscribe(sub_id, user_email):
        return response_handler({'message': f'Unsubscribed successfully!'}, 200)
    else:
        return response_handler({'message': ISSUE_MSG}, status=400)