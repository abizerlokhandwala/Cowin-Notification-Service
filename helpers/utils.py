import json

from datetime import date, timedelta

from helpers.constants import BOTH, COVAXIN, COVISHIELD, ABOVE_18, ABOVE_45, ABOVE_18_COWIN, ABOVE_45_COWIN
from helpers.cowin_sdk import CowinAPI


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
    weeks = 2
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
                        'slots': session['slots']
                    })
    return centers