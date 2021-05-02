import logging
import os
import uuid

import pymysql

from helpers.constants import GET_USER_QUERY, ADD_USER_QUERY, SUBSCRIPTION_EXISTS, ADD_SUBSCRIPTION, \
    ADD_USER_SUBSCRIPTION, UNSUBSCRIBE_USER_SUBSCRIPTION


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
            verification_token = uuid.uuid4()
            try:
                cursor.execute(ADD_USER_QUERY, (email, verification_token, 0, phone_number))
                user_id = self.connection.insert_id()
                self.connection.commit()
            except pymysql.err.IntegrityError:
                cursor.close()
                return -1
        else:
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

    def unsubscribe(self, sub_id, email):
        try:
            cursor = self.connection.cursor()
            cursor.execute(UNSUBSCRIBE_USER_SUBSCRIPTION, (email, sub_id))
            self.connection.commit()
            cursor.close()
        except Exception as e:
            logging.error(e, exc_info=True)
            return False
        return True