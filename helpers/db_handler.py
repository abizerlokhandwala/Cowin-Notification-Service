import logging
import os
import uuid

import pymysql
import requests

from helpers.constants import GOOGLE_GEOCODE_URL, GMAPS_API_KEY
from helpers.queries import GET_USER_QUERY, ADD_USER_QUERY, DISTRICT_SUBSCRIPTION_EXISTS, DISTRICT_ADD_SUBSCRIPTION, \
    ADD_USER_SUBSCRIPTION, UNSUBSCRIBE_USER_SUBSCRIPTION, GET_CANDIDATE_DISTRICTS, \
    GET_HISTORICAL_DATA, GET_PROCESSED_DISTRICTS, PINCODE_SUBSCRIPTION_EXISTS, PINCODE_ADD_SUBSCRIPTION, \
    GET_PINCODE_LOCATION, INSERT_PINCODE_LOCATION

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class DBHandler:

    __instance = None

    def __init__(self):
        self.connection = pymysql.connect(
            host=os.getenv('DB_HOSTNAME'),
            port=int(os.getenv('DB_PORT')),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'))
        # DBHandler.__instance = self

    @staticmethod
    def get_instance():
        # if DBHandler.__instance is None:
        return DBHandler()
        # return DBHandler.__instance

    def subscribe(self, body):
        email = body['email']
        phone_number = body['phone_number']
        cursor = self.connection.cursor()
        cursor.execute(GET_USER_QUERY, (email,))
        row = cursor.fetchone()
        verified = True
        verification_token = None
        if not row:
            verified = False
            verification_token = str(uuid.uuid4())
            try:
                cursor.execute(ADD_USER_QUERY, (email, verification_token, 0, phone_number))
                user_id = self.connection.insert_id()
                self.connection.commit()
            except pymysql.err.IntegrityError:
                cursor.close()
                return -1
        else:
            if int(row[3]) == 0:
                verified = False
                verification_token = row[2]
            user_id = row[0]

        subscription_ids = []
        for subscription in body['subscriptions']:
            dose_1 = 0
            dose_2 = 0
            if subscription['dose'] == 'dose_1':
                dose_1 = 1
            elif subscription['dose'] == 'dose_2':
                dose_2 = 1

            if subscription['type'] == 'district':
                cursor.execute(DISTRICT_SUBSCRIPTION_EXISTS, (subscription['district_id'], subscription['age_group'], subscription['vaccine'], dose_1, dose_2))
                row = cursor.fetchall()
                if not row:
                    cursor.execute(DISTRICT_ADD_SUBSCRIPTION, (subscription['district_id'], subscription['age_group'], subscription['vaccine'], dose_1, dose_2))
                    subscription_ids.append(self.connection.insert_id())
                    self.connection.commit()
                else:
                    subscription_ids.append(row[0][0])
            elif subscription['type'] == 'pincode':
                subscription['pincode_distance'] = 1000*int(subscription['pincode_distance']) # convert km to meters
                cursor.execute(PINCODE_SUBSCRIPTION_EXISTS,
                               (subscription['pincode'], subscription['pincode_distance'], subscription['age_group'], subscription['vaccine'], dose_1, dose_2))
                row = cursor.fetchall()
                if not row:
                    location = get_pin_code_location(subscription['pincode'])
                    if location == "POINT (-1 -1)":
                        return -2, None
                    cursor.execute(PINCODE_ADD_SUBSCRIPTION,
                                   (subscription['pincode'], subscription['pincode_distance'],
                                    location, subscription['age_group'], subscription['vaccine'], dose_1, dose_2))
                    subscription_ids.append(self.connection.insert_id())
                    self.connection.commit()
                else:
                    subscription_ids.append(row[0][0])

        for sub_id in subscription_ids:
            cursor.execute(ADD_USER_SUBSCRIPTION, (user_id, sub_id, 'email'))

        self.connection.commit()
        cursor.close()
        return verified, verification_token

    def unsubscribe(self, email, token):
        try:
            cursor = self.connection.cursor()
            cursor.execute(UNSUBSCRIBE_USER_SUBSCRIPTION, (email,token))
            self.connection.commit()
            cursor.close()
        except Exception as e:
            logger.error(e, exc_info=True)
            return False
        return True

    def candidate_districts(self):
        try:
            cursor = self.connection.cursor()
            cursor.execute(GET_CANDIDATE_DISTRICTS)
            rows = cursor.fetchall()
            district_id_list = [ele[0] for ele in rows]
            cursor.close()
            return district_id_list
        except Exception as e:
            logger.error(e, exc_info=True)
        return

    def district_subscriptions(self):
        try:
            cursor = self.connection.cursor()
            cursor.execute(GET_CANDIDATE_DISTRICTS)
            rows = cursor.fetchall()
            district_id_list = [ele[0] for ele in rows]
            cursor.close()
            return district_id_list
        except Exception as e:
            logger.error(e, exc_info=True)
        return

    def get_historical_data(self, date_from):
        try:
            cursor = self.connection.cursor()
            # cursor.execute(GET_HISTORICAL_DATA,(district_id, date_from, district_id, date_from, time_added_from))
            cursor.execute(GET_HISTORICAL_DATA, (date_from,))
            rows = cursor.fetchall()
            cursor.close()
            rows = set([row[0] for row in rows])
            return rows
        except Exception as e:
            logger.error(e, exc_info=True)
        return

    def insert(self, query, params):
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            self.connection.commit()
            cursor.close()
            return True
        except Exception as e:
            logger.error(e, exc_info=True)
        return False

    def is_district_processed(self, district_id):
        cursor = self.connection.cursor()
        cursor.execute(GET_PROCESSED_DISTRICTS, (district_id,))
        row = cursor.fetchone()
        cursor.close()
        if row:
            return True
        return False

    def query(self, query, params):
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        cursor.close()
        return rows

    def close(self):
        self.connection.close()
        return

def get_pin_code_location(pin_code: str) -> str:
    db = DBHandler.get_instance()
    rows = db.query(GET_PINCODE_LOCATION, (pin_code,))
    if len(rows) == 1:
        lat = rows[0][1]
        lng = rows[0][2]
        db.close()
    else:
        r = requests.get(GOOGLE_GEOCODE_URL, {'address': pin_code, 'key': GMAPS_API_KEY})
        r.raise_for_status()
        data = r.json()
        if len(data['results']) > 0:
            coordinates = data['results'][0]['geometry']['location']
            lat = coordinates['lat']
            lng = coordinates['lng']
            db.insert(INSERT_PINCODE_LOCATION, (pin_code, lat, lng))
            db.close()
        else:
            logger.info(f'Pincode: {pin_code}')
            db.close()
            return "POINT (-1 -1)"
            # raise ValueError('No address returned by geocode api')
    return f"POINT({lat} {lng})"
