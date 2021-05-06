import json
import logging
import os

from helpers.constants import ISSUE_MSG
from helpers.cowin_sdk import CowinAPI
from helpers.db_handler import DBHandler
from helpers.decorators import validate_args
from helpers.notificationHandler import NotifHandler
from helpers.queries import USER_PATTERN_MATCH, GET_USER_QUERY, UPDATE_USER_VERIFIED
from helpers.utils import response_handler, get_preference_slots, sqs, send_historical_diff
from datetime import date

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
    return response_handler(get_preference_slots(district_id, vaccine, age_group),200)

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
    db = DBHandler.get_instance()
    if db.unsubscribe(user_email):
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
    for district in districts:
        if district:
            logger.info(f'District: {district}')
            sqs.send_message(MessageBody=json.dumps({'district':district}), QueueUrl=os.getenv('DISTRICT_QUEUE_URL'))
            logger.info(f'Sent district_id {district} to DISTRICT_QUEUE')
    return response_handler({},200)

def update_district_slots(event, context):
    processed_districts = set()
    logger.info(f'Event: {event}')
    for record in event['Records']:
        district_id = json.loads(record['body'])['district']
        send_historical_diff(district_id)
        processed_districts.add(district_id)
        sqs.delete_message(ReceiptHandle=record['receiptHandle'], QueueUrl=os.getenv('DISTRICT_QUEUE_URL'))
    return response_handler({'message': f'Districts {processed_districts} processed'},200)

def notif_dispatcher(event, context):
    notif = NotifHandler()
    db = DBHandler.get_instance()
    logger.info(f'Event: {event}')
    for record in event['Records']:
        message = json.loads(record['body'])
        logger.info(f'message: {message}')
        user_emails = [row[0] for row in db.query(USER_PATTERN_MATCH,('email',message['district_id'],message['age_group'],message['vaccine']))]
        logger.info(f'Users to send emails to: {user_emails}')
        notif.send_emails(user_emails, message)
        sqs.delete_message(ReceiptHandle=record['receiptHandle'], QueueUrl=os.getenv('NOTIF_QUEUE_URL'))
    return response_handler({'message': f'All notifs processed'},200)