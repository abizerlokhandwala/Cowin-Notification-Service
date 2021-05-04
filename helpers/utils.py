import json
import os

from datetime import date, timedelta

import boto3

from helpers.constants import BOTH, COVAXIN, COVISHIELD, ABOVE_18, ABOVE_45, ABOVE_18_COWIN, ABOVE_45_COWIN, NUM_WEEKS
from helpers.cowin_sdk import CowinAPI
from helpers.db_handler import DBHandler
from helpers.queries import ADD_DISTRICT_PROCESSED, ADD_PROCESSED_DISTRICTS

sqs = boto3.client('sqs', region_name='ap-south-1')

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
    centers = {}
    for week in range(0,weeks):
        itr_date = (date.today() + timedelta(weeks=week)).strftime("%d-%m-%Y")
        response = cowin.get_centers_7(district_id, itr_date)
        for center in response:
            for session in center['sessions']:
                if session['available_capacity']>0 and pattern_match(vaccine, age_group, session['vaccine'], session['min_age_limit']):
                    if center['name'] not in centers:
                        centers[center['name']] = []
                    centers[center['name']].append({
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

def send_historical_diff(district_id):
    cowin = CowinAPI()
    db = DBHandler.get_instance()
    weeks = NUM_WEEKS
    db_data = db.get_historical_data(district_id, date.today().strftime("%d-%m-%Y"))
    is_district_processed = db.is_district_processed(district_id)
    for week in range(0,weeks):
        itr_date = (date.today() + timedelta(weeks=week)).strftime("%d-%m-%Y")
        response = cowin.get_centers_7(district_id, itr_date)
        for center in response:
            for session in center['sessions']:
                if session['available_capacity'] > 0:
                    if get_historical_ds(district_id, center['center_id'], session['date'], session['min_age_limit']
                                          ,get_vaccine(session['vaccine'])) in db_data:
                        continue
                    db.insert(ADD_DISTRICT_PROCESSED, (district_id, center['center_id'], session['date'], session['min_age_limit']
                                          ,get_vaccine(session['vaccine'])))
                    if is_district_processed:
                        message = {
                            'district_id': district_id,
                            'center_id': center['center_id'],
                            'center_name':  center['name'],
                            'address': center['address'],
                            'district_name': center['district_name'],
                            'pincode': center['pincode'],
                            'from': center['from'],
                            'to': center['to'],
                            'fee_type': center['fee_type'],
                            'date': session['date'],
                            'age_group': f'above_{session["min_age_limit"]}',
                            'vaccine': get_vaccine(session['vaccine']),
                            'slots': session['slots'],
                            'capacity': session['available_capacity']
                        }
                        sqs.send_message(MessageBody=json.dumps(message), QueueUrl=os.getenv('NOTIF_QUEUE_URL'))
    if not is_district_processed:
        db.insert(ADD_PROCESSED_DISTRICTS,(district_id,))
    return