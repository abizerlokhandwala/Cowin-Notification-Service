import asyncio
import json
import logging
import os
import random
import uuid
from datetime import date
import boto3
import requests

from helpers.constants import ISSUE_MSG
from helpers.cowin_sdk import CowinAPI
from helpers.db_handler import DBHandler
from helpers.notificationHandler import NotifHandler
from helpers.queries import USER_PATTERN_MATCH, GET_USER_QUERY, UPDATE_USER_VERIFIED
from helpers.utils import response_handler, get_preference_slots, sqs, send_historical_diff, calculate_hash_int, \
    get_event_loop

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
    db = DBHandler.get_instance()
    notif = NotifHandler()
    is_verified, verification_token = db.subscribe(body)
    if is_verified == -1:
        return response_handler({'message': f'Email Already exists'}, 400)
    additional_comments = ''
    if is_verified is False:
        notif.send_verification_email(body['email'])
        additional_comments = f'Please verify your email ID: {body["email"]}'
    return response_handler({'message': f'Subscribed successfully! {additional_comments}'}, 201)


def unsubscribe(event, context):
    user_email = event["queryStringParameters"]["email"]
    token = event["queryStringParameters"]["token"]
    db = DBHandler.get_instance()
    if db.unsubscribe(user_email, token):
        return response_handler({'message': f'Unsubscribed successfully!'}, 200)
    else:
        return response_handler({'message': ISSUE_MSG}, status=400)


def verify_email(event, context):
    user_email = event["queryStringParameters"]["email"]
    token = event["queryStringParameters"]["token"]
    db = DBHandler.get_instance()
    user = db.query(GET_USER_QUERY, (user_email,))
    if user and int(user[0][3]) == 1:
        return response_handler({'message': 'User already verified'}, status=200)
    if user and user[0][2] == token:
        db.insert(UPDATE_USER_VERIFIED, (user_email,))
        return response_handler({'message': 'Successful Verification'}, status=200)
    return response_handler({'message': 'Unsuccessful Verification'}, status=403)


def trigger_district_updates(event, context):
    db = DBHandler.get_instance()
    districts = db.candidate_districts()
    client = boto3.client('lambda', region_name='ap-south-1')
    UPDATE_FUNCTION_NAME = 'cowin-notification-service-dev-update_district_slots'
    batch = []
    for district in districts:
        if district:
            batch.append(district)
            if len(batch)>=30:
                client.invoke(FunctionName=UPDATE_FUNCTION_NAME,
                                     InvocationType='Event', Payload=json.dumps({'districts': batch}))
                batch.clear()
    if len(batch) > 0:
        client.invoke(FunctionName=UPDATE_FUNCTION_NAME,
                      InvocationType='Event', Payload=json.dumps({'districts': batch}))
    return response_handler({},200)


def update_district_slots(event, context):
    processed_districts = set()
    # logger.info(f"IP: {requests.get('https://api.ipify.org').text}")
    district_ids = event['districts']
    # district_ids = [363]
    get_event_loop().run_until_complete(asyncio.gather(*[send_historical_diff(district_id) for district_id in
                                                             district_ids]))
    processed_districts |= district_ids
    return response_handler({'message': f'Districts {processed_districts} processed'}, 200)

def notif_dispatcher(event, context):
    notif = NotifHandler()
    db = DBHandler.get_instance()
    for record in event['Records']:
        message = json.loads(record['body'])
        user_info = [(row[0], row[1]) for row in db.query(USER_PATTERN_MATCH, (
            'email', message['district_id'], message['age_group'], message['vaccine']))]
        # logger.info(f'Users to send emails to: {user_info}')
        message['age_group'] += '+'
        message['age_group'] = message['age_group'].replace('above_', '')
        notif.send_template_emails(user_info, message)
        sqs.delete_message(ReceiptHandle=record['receiptHandle'], QueueUrl=os.getenv('NOTIF_QUEUE_URL'))
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
            'capacity': '5',
            'fee_type': 'free'
        })
    return
