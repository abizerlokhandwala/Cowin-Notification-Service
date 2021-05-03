from helpers.constants import DB_NAME

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
GET_CANDIDATE_DISTRICTS = (f'SELECT distinct district_id from {DB_NAME}.subscriptions '
                           f'where id in (SELECT subscription_id from {DB_NAME}.user_subscriptions where '
                           f'is_subscribed = 1 and user_id in (SELECT id from {DB_NAME}.users where is_verified = 1))')
ADD_DISTRICT_PROCESSED = (f'INSERT INTO {DB_NAME}.historical_slot_data '
                          f'(district_id, center_id, date, age_group, vaccine) '
                          f'values (%s, %s, %s, %s, %s)')
GET_HISTORICAL_DATA = (f'SELECT district_id, center_id, date, age_group, LOWER(vaccine) from {DB_NAME}.historical_slot_data '
                           f'where district_id = %s and date>= %s')