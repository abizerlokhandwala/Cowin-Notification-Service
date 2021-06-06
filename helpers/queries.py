from helpers.constants import DB_NAME

GET_USER_QUERY = f'SELECT * FROM {DB_NAME}.users where email = %s'
ADD_USER_QUERY = (f'INSERT INTO {DB_NAME}.users '
                  '(email, email_verification_token, is_verified, phone_number)'
                  'values (%s, %s, %s, %s)')
SUBSCRIPTION_EXISTS = f'SELECT id from {DB_NAME}.subscriptions where district_id = %s and age_group = %s and vaccine = %s'
ADD_SUBSCRIPTION = (f'INSERT IGNORE INTO {DB_NAME}.subscriptions'
                    '(district_id, age_group, vaccine)'
                    'values (%s, %s, %s)')
ADD_USER_SUBSCRIPTION = (f'INSERT INTO {DB_NAME}.user_subscriptions'
                         '(user_id, subscription_id, type, is_subscribed)'
                         'values (%s, %s, %s, 1)'
                         'ON DUPLICATE KEY UPDATE is_subscribed = 1')
UNSUBSCRIBE_USER_SUBSCRIPTION = (f'UPDATE {DB_NAME}.user_subscriptions SET is_subscribed = 0 '
                                 f'where user_id = (SELECT id from {DB_NAME}.users where email = %s and email_verification_token = %s)')
GET_PROCESSED_DISTRICTS = (f'SELECT district_id from {DB_NAME}.processed_districts '
                           f'where district_id = %s')
ADD_PROCESSED_DISTRICTS = (f'INSERT IGNORE INTO {DB_NAME}.processed_districts '
                           f'values(%s)')
GET_CANDIDATE_DISTRICTS = (f'SELECT distinct district_id from {DB_NAME}.subscriptions '
                           f'where id in (SELECT subscription_id from {DB_NAME}.user_subscriptions where '
                           f'is_subscribed = 1 and user_id in (SELECT id from {DB_NAME}.users where is_verified = 1))')
ADD_DISTRICT_PROCESSED = (f'INSERT INTO {DB_NAME}.historical_slot_data '
                          f'(district_id, center_id, date, age_group, vaccine, time_added) '
                          f'values (%s, %s, %s, %s, %s, %s)')
# GET_HISTORICAL_DATA = (f'SELECT district_id, center_id, date, age_group, LOWER(vaccine) from {DB_NAME}.historical_slot_data '
#                        f'where district_id = %s and date > %s'
#                        f'UNION SELECT district_id, center_id, date, age_group, LOWER(vaccine) from {DB_NAME}.historical_slot_data '
#                        f'where district_id = %s and date = %s and time_added >= %s')
GET_HISTORICAL_DATA = (f'SELECT district_id, center_id, date, age_group, LOWER(vaccine) from {DB_NAME}.historical_slot_data '
                       f'where district_id = %s and date >= %s')
USER_PATTERN_MATCH = (
    f'SELECT distinct email, email_verification_token from {DB_NAME}.users where is_verified = 1 and id in '
    f'(SELECT user_id from {DB_NAME}.user_subscriptions where is_subscribed = 1 and type = %s '
    f'and subscription_id in (SELECT id from {DB_NAME}.subscriptions where '
    f'age_group in (%s, "both") and vaccine in (%s, "both") and (district_id=%s or ST_Distance_Sphere'
    f'(location, ST_GeomFromText(%s, 4326)) < max_distance)))')

ADD_USER_TOKEN = f'UPDATE {DB_NAME}.users SET email_verification_token = %s where email = %s'
UPDATE_USER_VERIFIED = f'UPDATE {DB_NAME}.users SET is_verified = 1 where email = %s'
GET_PINCODE_LOCATION = f'SELECT * FROM {DB_NAME}.pincodes WHERE pincode = %s'
INSERT_PINCODE_LOCATION = f'INSERT INTO {DB_NAME}.pincodes(pincode, latitude, longitude) VALUES(%s, %s, %s)'
