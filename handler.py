import json
import logging
import os

from helpers.constants import ISSUE_MSG
from helpers.cowin_sdk import CowinAPI
from helpers.db_handler import DBHandler
from helpers.decorators import validate_args
from helpers.email_handler import EmailHandler
from helpers.notificationHandler import NotifHandler
from helpers.queries import USER_PATTERN_MATCH
from helpers.utils import response_handler, get_preference_slots, sqs, send_historical_diff
from datetime import date

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
    return response_handler(get_preference_slots(district_id, vaccine, age_group),200)

def subscribe(event, context):
    body = json.loads(event['body'])
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
    user_email = event["queryStringParameters"]["email"]
    db = DBHandler.get_instance()
    if db.unsubscribe(user_email):
        return response_handler({'message': f'Unsubscribed successfully!'}, 200)
    else:
        return response_handler({'message': ISSUE_MSG}, status=400)

def trigger_district_updates(event, context):
    db = DBHandler.get_instance()
    districts = db.candidate_districts()
    for district in districts:
        if district:
            sqs.send_message(MessageBody=district, QueueUrl=os.getenv('DISTRICT_QUEUE_URL'))
            logging.info(f'Sent district_id {district} to DISTRICT_QUEUE')
    return response_handler({},200)

def update_district_slots(event, context):
    processed_districts = ''
    for record in event['Records']:
        district_id = record['body']
        send_historical_diff(district_id)
        processed_districts+=district_id+' '
        sqs.delete_message(ReceiptHandle=record['receiptHandle'], QueueUrl=os.getenv('DISTRICT_QUEUE_URL'))
    return response_handler({'message': f'Districts {processed_districts} processed'},200)

def notif_dispatcher(event, context):
    count = 0
    notif = NotifHandler()
    db = DBHandler.get_instance()
    for record in event['Records']:
        message = json.loads(record['body'])
        user_emails = [row[0] for row in db.query(USER_PATTERN_MATCH,('email',message['district_id'],message['age_group'],message['vaccine']))]
        notif.send_emails(user_emails, message)
        count+=1
        sqs.delete_message(ReceiptHandle=record['receiptHandle'], QueueUrl=os.getenv('NOTIF_QUEUE_URL'))
    return response_handler({'message': f'{count} notifs processed'},200)