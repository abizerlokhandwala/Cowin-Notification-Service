import os

COWIN_URL = 'https://cdn-api.co-vin.in/api/v2/'
STATES_URL = f'{COWIN_URL}admin/location/states/'
DISTRICTS_URL = f'{COWIN_URL}admin/location/districts/'
CALENDAR_BY_DISTRICT_URL = f'{COWIN_URL}appointment/sessions/public/calendarByDistrict/'

BOTH = 'both'
COVISHIELD = 'covishield'
COVAXIN = 'covaxin'
ABOVE_18 = 'above_18'
ABOVE_45 = 'above_45'
ABOVE_18_COWIN = '18'
ABOVE_45_COWIN = '45'

DB_NAME = os.getenv('DB_NAME')
# DB_NAME = 'cowin_data'
ISSUE_MSG = 'There was an issue with your request, please contact the developers'

NUM_WEEKS = 2