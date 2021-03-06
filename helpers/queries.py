from helpers.constants import DB_NAME

GET_USER_QUERY = f'SELECT * FROM {DB_NAME}.users where email = %s'
ADD_USER_QUERY = (f'INSERT INTO {DB_NAME}.users '
                  '(email, email_verification_token, is_verified, phone_number)'
                  'values (%s, %s, %s, %s)')
DISTRICT_SUBSCRIPTION_EXISTS = f'SELECT id from {DB_NAME}.subscriptions where district_id = %s and age_group = %s and vaccine = %s and dose_1 = %s and dose_2 = %s'
PINCODE_SUBSCRIPTION_EXISTS = f'SELECT id from {DB_NAME}.subscriptions where pincode = %s and max_distance = %s and age_group = %s and vaccine = %s and dose_1 = %s and dose_2 = %s'
DISTRICT_ADD_SUBSCRIPTION = (f'INSERT IGNORE INTO {DB_NAME}.subscriptions'
                    '(district_id, age_group, vaccine, dose_1, dose_2)'
                    'values (%s, %s, %s, %s, %s)')
PINCODE_ADD_SUBSCRIPTION = (f'INSERT IGNORE INTO {DB_NAME}.subscriptions'
                    '(pincode, max_distance, location, age_group, vaccine, dose_1, dose_2)'
                    'values (%s, %s, ST_GeomFromText(%s, 4326), %s, %s, %s, %s)')
ADD_USER_SUBSCRIPTION = (f'INSERT INTO {DB_NAME}.user_subscriptions'
                         '(user_id, subscription_id, type, is_subscribed, date)'
                         'values (%s, %s, %s, 1, %s)')
UNSUBSCRIBE_USER_SUBSCRIPTION = (f'UPDATE {DB_NAME}.user_subscriptions SET is_subscribed = 0 '
                                 f'where user_id = (SELECT id from {DB_NAME}.users where email = %s and email_verification_token = %s)')
GET_PROCESSED_DISTRICTS = (f'SELECT district_id from {DB_NAME}.processed_districts '
                           f'where district_id = %s')
ADD_PROCESSED_DISTRICTS = (f'INSERT IGNORE INTO {DB_NAME}.processed_districts '
                           f'values(%s)')
GET_CANDIDATE_DISTRICTS = f'SELECT distinct district_id from {DB_NAME}.subscriptions'
ADD_DISTRICT_PROCESSED = (f'INSERT INTO {DB_NAME}.historical_slot_data '
                          f'(district_id, center_id, date, age_group, vaccine, session_id) '
                          f'values (%s, %s, %s, %s, %s, %s)')
# GET_HISTORICAL_DATA = (f'SELECT district_id, center_id, date, age_group, LOWER(vaccine) from {DB_NAME}.historical_slot_data '
#                        f'where district_id = %s and date > %s'
#                        f'UNION SELECT district_id, center_id, date, age_group, LOWER(vaccine) from {DB_NAME}.historical_slot_data '
#                        f'where district_id = %s and date = %s and time_added >= %s')
GET_HISTORICAL_DATA = (f'SELECT session_id from {DB_NAME}.historical_slot_data '
                       f'where district_id = %s and date >= %s')
USER_PATTERN_MATCH = (
    f'SELECT distinct email, email_verification_token from {DB_NAME}.users where is_verified = 1 and id in '
    f'(SELECT user_id from {DB_NAME}.user_subscriptions where is_subscribed = 1 and type = %s '
    f'and subscription_id in (SELECT id from {DB_NAME}.subscriptions where '
    f'age_group in (%s, "both") and vaccine in (%s, "both") and (dose_1 = %s or dose_2 = %s) and (district_id=%s or ST_Distance_Sphere'
    f'(location, ST_GeomFromText(%s, 4326)) < max_distance)))')

ADD_USER_TOKEN = f'UPDATE {DB_NAME}.users SET email_verification_token = %s where email = %s'
UPDATE_USER_VERIFIED = f'UPDATE {DB_NAME}.users SET is_verified = 1 where email = %s'
GET_PINCODE_LOCATION = f'SELECT * FROM {DB_NAME}.pincodes WHERE pincode = %s'
INSERT_PINCODE_LOCATION = f'INSERT INTO {DB_NAME}.pincodes(pincode, latitude, longitude) VALUES(%s, %s, %s)'

SUBSCRIBED_DISTRICT_USERS = (
    f'SELECT distinct email, email_verification_token from {DB_NAME}.users where is_verified = 1 and id in '
    f'(SELECT user_id from {DB_NAME}.user_subscriptions where is_subscribed = 1 and type = %s '
    f'and subscription_id in (SELECT id from {DB_NAME}.subscriptions where '
    f'district_id != "NA"))')

