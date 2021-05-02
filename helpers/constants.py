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

ISSUE_MSG = 'There was an issue with your request, please contact the developers'

GET_USER_QUERY = f'SELECT * FROM {DB_NAME}.users where email = %s'
ADD_USER_QUERY = (f'INSERT INTO {DB_NAME}.users '
                  '(email, email_verification_token, is_verified, phone_number)'
                  'values (%s, %s, %s, %s)')
SUBSCRIPTION_EXISTS = f'SELECT id from {DB_NAME}.subscriptions where district_id = %s and age_group = %s and vaccine = %s'
ADD_SUBSCRIPTION = (f'INSERT IGNORE INTO {DB_NAME}.subscriptions'
                    '(district_id, age_group, vaccine)'
                    'values (%s, %s, %s)')
ADD_USER_SUBSCRIPTION = (f'INSERT IGNORE INTO {DB_NAME}.user_subscriptions'
                    '(user_id, subscription_id, type)'
                    'values (%s, %s, %s)')
UNSUBSCRIBE_USER_SUBSCRIPTION = (f'UPDATE {DB_NAME}.user_subscriptions SET is_subscribed = 0 ' 
                                 f'where user_id = (SELECT id from {DB_NAME}.users where email = %s) '
                                 'and subscription_id = %s')
