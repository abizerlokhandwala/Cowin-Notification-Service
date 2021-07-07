import asyncio
import json
import logging
import random
from datetime import date

import boto3

from helpers.constants import ISSUE_MSG, DB_NAME
from helpers.cowin_sdk import CowinAPI
from helpers.db_handler import DBHandler, get_pin_code_location
from helpers.notificationHandler import NotifHandler
from helpers.queries import USER_PATTERN_MATCH, GET_USER_QUERY, UPDATE_USER_VERIFIED, SUBSCRIBED_DISTRICT_USERS
from helpers.utils import response_handler, get_preference_slots, send_historical_diff, get_event_loop

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


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
    date_today = date.today().strftime("%d-%m-%Y")
    centers = cowin.get_centers_7(district_id, date_today)
    return response_handler(centers, 200)


def get_district_preferences(event, context):
    district_id = event["queryStringParameters"]['district_id']
    vaccine = event["queryStringParameters"]['vaccine']
    age_group = event["queryStringParameters"]['age_group']
    return response_handler(get_preference_slots(district_id, vaccine, age_group), 200)


def subscribe(event, context):
    body = json.loads(event['body'])
    body['email'] = body['email'].strip()
    db = DBHandler.get_instance()
    notif = NotifHandler()
    is_verified, verification_token = db.subscribe(body)
    if is_verified == -1:
        return response_handler({'message': f'Email Already exists'}, 400)
    elif is_verified == -2: # pincode not found
        return response_handler({'message': f'Pincode is invalid'}, 400)
    additional_comments = ''
    if is_verified is False:
        notif.send_verification_email(body['email'], True)
        additional_comments = f'Please verify your email ID: {body["email"]}'
    db.close()
    return response_handler({'message': f'Subscribed successfully! {additional_comments}'}, 201)


def unsubscribe(event, context):
    user_email = event["queryStringParameters"]["email"]
    token = event["queryStringParameters"]["token"]
    db = DBHandler.get_instance()
    if db.unsubscribe(user_email, token):
        logger.info(f'{user_email} unsubscribed')
        db.close()
        return response_handler({'message': f'Unsubscribed successfully!'}, 200)
    else:
        db.close()
        return response_handler({'message': ISSUE_MSG}, status=400)


def verify_email(event, context):
    user_email = event["queryStringParameters"]["email"]
    token = event["queryStringParameters"]["token"]
    db = DBHandler.get_instance()
    user = db.query(GET_USER_QUERY, (user_email,))
    if user and int(user[0][3]) == 1:
        db.close()
        return response_handler({'message': 'User already verified'}, status=200)
    if user and user[0][2] == token:
        db.insert(UPDATE_USER_VERIFIED, (user_email,))
        db.close()
        return response_handler({'message': 'Successful Verification'}, status=200)
    db.close()
    return response_handler({'message': 'Unsuccessful Verification'}, status=403)

def check_district_nums(event, context):
    cowin = CowinAPI()
    districts = cowin.get_all_districts()
    for ind in range(0,1+max(districts)):
        if ind not in districts:
            print(f'Missing {ind}')
    return districts

district_nums = []

def trigger_district_updates(event, context):
    global district_nums
    # db = DBHandler.get_instance()
    # districts = db.candidate_districts()
    # db.close()
    if not district_nums:
        cowin = CowinAPI()
        district_nums = cowin.get_all_districts()
    client = boto3.client('lambda', region_name='ap-south-1')
    UPDATE_FUNCTION_NAME = 'cowin-notification-service-dev-update_district_slots'
    batch = []
    for district in district_nums:
        if district:
            batch.append(district)
            if len(batch) >= 10:
                client.invoke(FunctionName=UPDATE_FUNCTION_NAME,
                              InvocationType='Event', Payload=json.dumps({'districts': batch}))
                batch.clear()
    if len(batch) > 0:
        client.invoke(FunctionName=UPDATE_FUNCTION_NAME,
                      InvocationType='Event', Payload=json.dumps({'districts': batch}))
    return response_handler({}, 200)


def update_district_slots(event, context):
    # logger.info(f"IP: {requests.get('https://api.ipify.org').text}")
    district_ids = event['districts']
    # district_ids = [363]
    get_event_loop().run_until_complete(asyncio.gather(*[send_historical_diff(district_id) for district_id in
                                                         district_ids]))
    return response_handler({'message': f'Districts {district_ids} processed'}, 200)


def notif_dispatcher(event, context):
    message = event['message']
    # message = {'vaccine':'covishield','age_group':'above_18','district_id':'363','pincode':'411028'}
    location = get_pin_code_location(message['pincode'])
    db = DBHandler.get_instance()
    user_info = [(row[0], row[1]) for row in db.query(USER_PATTERN_MATCH, (
        'email', message['age_group'], message['vaccine'], message['dose_1'], message['dose_2'],
         message['district_id'], location))]
    db.close()
    # print(user_info)
    # return {}
    # logger.info(f'Users to send emails to: {user_info}')
    message['age_group'] += '+'
    message['age_group'] = message['age_group'].replace('above_', '')
    client = boto3.client('lambda', region_name='ap-south-1')
    SEND_EMAIL_FUNCTION_NAME = 'cowin-notification-service-dev-send_batch_email'
    batch = []
    for user in user_info:
        if user:
            batch.append(user)
            if len(batch) >= 20:
                client.invoke(FunctionName=SEND_EMAIL_FUNCTION_NAME,
                                     InvocationType='Event', Payload=json.dumps({'users': batch, 'message': message}))
                batch.clear()
    if len(batch) > 0:
        client.invoke(FunctionName=SEND_EMAIL_FUNCTION_NAME,
                      InvocationType='Event', Payload=json.dumps({'users': batch, 'message': message}))
    return response_handler({},200)

def send_batch_email(event, context):
    notif = NotifHandler()
    users = event['users']
    message = event['message']
    notif.send_template_emails(users, message)
    return response_handler({'message': f'All notifs processed'}, 200)

def test_email(event, context):
    notif = NotifHandler()
    notif.send_template_emails(
        [('abizerL123@gmail.com', 'abc'), ('sharangpai123@gmail.com', 'abc'), ('pujan.iceman@gmail.com', 'abc'),
         ('shloksingh10@gmail.com', 'abc'), ('arsenal.arpit11@gmail.com', 'abc')], {
            'center_name': 'test_center',
            'slots': '[1-2]',
            'district_name': 'test_district',
            'date': '1-1-1',
            'age_group': '45',
            'vaccine': 'covishield',
            'address': 'abc, pqr, xyz',
            'pincode': '411040',
            'capacity': '40',
            'capacity_dose_1': '20',
            'capacity_dose_2': '20',
            'fee_amount': '₹200'
        })
    return

def notify_pincode_email(event, context):
    db = DBHandler.get_instance()
    user_info = [(row[0], row[1]) for row in db.query(SUBSCRIBED_DISTRICT_USERS, (
        'email'))]
    db.close()
    notif = NotifHandler()
    notif.send_pincode_one_time_email(user_info)
    return

def test_email_pincode(event, context):
    notif = NotifHandler()
    notif.send_pincode_one_time_email(
        [('abizerL123@gmail.com', 'abc'), ('sharangpai123@gmail.com', 'abc'), ('pujan.iceman@gmail.com', 'abc'),
         ('shloksingh10@gmail.com', 'abc'), ('arsenal.arpit11@gmail.com', 'abc')])
    return

def send_verification_email_manual(event, context):
    db = DBHandler.get_instance()
    users = db.query(f"SELECT email FROM {DB_NAME}.users where id>=%s and is_verified = 0",(4923,))
    db.close()
    notif = NotifHandler()
    for user in users:
        notif.send_verification_email(user[0], False)
    return response_handler({'message': f'Sent'}, 200)

def poller_service_endpoint(event, context):
    body = event['body']
    logger.info(body)
    return response_handler({'message': 'success'},200)