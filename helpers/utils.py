import asyncio
import json
import logging
from datetime import date, timedelta, datetime

import boto3
import requests

from helpers.constants import BOTH, COVAXIN, COVISHIELD, ABOVE_18, ABOVE_45, ABOVE_18_COWIN, ABOVE_45_COWIN, NUM_WEEKS, \
    SPUTNIK, GOOGLE_GEOCODE_URL, GMAPS_API_KEY
from helpers.cowin_sdk import CowinAPI
from helpers.db_handler import DBHandler
from helpers.queries import ADD_DISTRICT_PROCESSED, ADD_PROCESSED_DISTRICTS, GET_PINCODE_LOCATION, \
    INSERT_PINCODE_LOCATION

sqs = boto3.client('sqs', region_name='ap-south-1')

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def response_handler(body, status):
    return {
        "statusCode": status,
        "body": json.dumps(body),
        "headers": {
            "Access-Control-Allow-Origin": "*"
        }
    }


def pattern_match(user_vaccine, user_age_group, vaccine, age_group):
    user_vaccine = user_vaccine.lower()
    user_age_group = user_age_group.lower()
    vaccine_bool = False
    age_bool = False

    if user_vaccine == BOTH:
        vaccine_bool = True
    elif user_vaccine == COVAXIN and vaccine in (COVAXIN, ''):
        vaccine_bool = True
    elif user_vaccine == COVISHIELD and vaccine == COVISHIELD:
        vaccine_bool = True
    elif user_vaccine == SPUTNIK and vaccine == SPUTNIK:
        vaccine_bool = True

    if user_age_group == BOTH:
        age_bool = True
    elif user_age_group == ABOVE_18 and str(age_group) == ABOVE_18_COWIN:
        age_bool = True
    elif user_age_group == ABOVE_45 and str(age_group) == ABOVE_45_COWIN:
        age_bool = True

    return vaccine_bool and age_bool


def get_preference_slots(district_id, vaccine, age_group):
    cowin = CowinAPI()
    weeks = NUM_WEEKS
    centers = []
    for week in range(0, weeks):
        itr_date = (date.today() + timedelta(weeks=week)).strftime("%d-%m-%Y")
        response = cowin.get_centers_7(district_id, itr_date)
        for center in response:
            for session in center['sessions']:
                if session['available_capacity'] > 0 and pattern_match(vaccine, age_group, session['vaccine'],
                                                                       session['min_age_limit']):
                    centers.append({
                        'center_name': center['name'],
                        'date': session['date'],
                        'capacity': session['available_capacity'],
                        'age_limit': session['min_age_limit'],
                        'vaccine': 'covaxin' if session['vaccine'] == '' else session['vaccine'],
                        'slots': session['slots'],
                        'pincode': center['pincode'],
                        'from': center['from'],
                        'to': center['to'],
                        'fee': center['fee_type']
                    })
    return centers


def get_historical_ds(district_id, center_id, date, age_group, vaccine):
    return str(district_id), str(center_id), str(date), str(age_group), str(vaccine)


def get_vaccine(vaccine):
    if vaccine == '':
        return COVAXIN
    else:
        return vaccine.lower()


async def send_historical_diff(district_id):
    cowin = CowinAPI()
    db = DBHandler.get_instance()
    weeks = NUM_WEEKS
    db_data = db.get_historical_data(district_id, date.today().strftime("%Y-%m-%d"))
    is_district_processed = db.is_district_processed(district_id)
    client = boto3.client('lambda', region_name='ap-south-1')
    NOTIF_FUNCTION_NAME = 'cowin-notification-service-dev-notif_dispatcher'
    for week in range(0, weeks):
        itr_date = (date.today() + timedelta(weeks=week))
        response = await cowin.get_centers_7_old(district_id, itr_date)
        for session in response:
            if session['available_capacity'] >= 10:
                if session['session_id'] in db_data or \
                        datetime.strptime(session['date'], '%d-%m-%Y').strftime('%Y-%m-%d') < itr_date.strftime('%Y-%m-%d'):
                    continue
                dose_1 = -1
                dose_2 = -1
                if session['available_capacity_dose1'] >= 10:
                    dose_1 = 1
                if session['available_capacity_dose2'] >= 10:
                    dose_2 = 1
                if dose_1 == -1 and dose_2 == -1:
                    continue
                if is_district_processed:
                    message = {
                        'district_id': district_id,
                        'center_id': session['center_id'],
                        'center_name': session['name'],
                        'address': session['address'],
                        'district_name': session['district_name'],
                        'pincode': session['pincode'],
                        'from': session['from'],
                        'to': session['to'],
                        'fee_type': session['fee_type'],
                        'fee_amount': session['fee_type'] if session['fee_type'].lower() == "free" else "₹"+session['fee'],
                        'date': session['date'],
                        'age_group': f'above_{session["min_age_limit"]}',
                        'vaccine': get_vaccine(session['vaccine']),
                        'slots': session['slots'],
                        'capacity': session['available_capacity'],
                        'capacity_dose_1': session['available_capacity_dose1'],
                        'capacity_dose_2': session['available_capacity_dose2'],
                        'dose_1': dose_1,
                        'dose_2': dose_2
                    }
                    client.invoke(FunctionName=NOTIF_FUNCTION_NAME,
                                  InvocationType='Event', Payload=json.dumps({'message': message}))
                db.insert(ADD_DISTRICT_PROCESSED, (district_id, session['center_id'],
                                                   datetime.strptime(session['date'], '%d-%m-%Y').strftime('%Y-%m-%d'),
                                                   session['min_age_limit'], get_vaccine(session['vaccine']),
                                                   session['session_id']))
    if not is_district_processed:
        db.insert(ADD_PROCESSED_DISTRICTS, (district_id,))
    db.close()
    return


def calculate_hash_int(msg_string):
    int_val = 0
    for ch in msg_string:
        int_val += ord(ch)
    return int_val


def get_event_loop():
    try:
        return asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop