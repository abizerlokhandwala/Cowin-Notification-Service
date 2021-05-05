import logging
import os
import uuid

import pymysql

from helpers.queries import GET_USER_QUERY, ADD_USER_QUERY, SUBSCRIPTION_EXISTS, ADD_SUBSCRIPTION, \
    ADD_USER_SUBSCRIPTION, UNSUBSCRIBE_USER_SUBSCRIPTION, GET_CANDIDATE_DISTRICTS, \
    GET_HISTORICAL_DATA, GET_PROCESSED_DISTRICTS

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
        DBHandler.__instance = self

    @staticmethod
    def get_instance():
        if DBHandler.__instance is None:
            DBHandler()
        return DBHandler.__instance

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
            cursor.execute(SUBSCRIPTION_EXISTS, (subscription['district_id'], subscription['age_group'], subscription['vaccine']))
            row = cursor.fetchall()
            if not row:
                cursor.execute(ADD_SUBSCRIPTION,(subscription['district_id'], subscription['age_group'], subscription['vaccine']))
                subscription_ids.append(self.connection.insert_id())
                self.connection.commit()
            else:
                subscription_ids.append(row[0][0])

        for sub_id in subscription_ids:
            cursor.execute(ADD_USER_SUBSCRIPTION, (user_id, sub_id, 'email'))

        self.connection.commit()
        cursor.close()
        return verified, verification_token

    def unsubscribe(self, email):
        try:
            cursor = self.connection.cursor()
            cursor.execute(UNSUBSCRIBE_USER_SUBSCRIPTION, (email,))
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

    def get_historical_data(self, district_id, date_from):
        try:
            cursor = self.connection.cursor()
            cursor.execute(GET_HISTORICAL_DATA,(district_id,date_from))
            rows = cursor.fetchall()
            cursor.close()
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