import logging
import os
import uuid

from helpers.constants import EMAIL_SUBJECT, EMAIL_BODY, VERIFY_EMAIL_BODY, VERIFY_SUBJECT, UNSUB_ENDPOINT, \
    TEMPLATE_DATA
from helpers.db_handler import DBHandler
from helpers.queries import ADD_USER_TOKEN, GET_USER_QUERY
from helpers.ses_handler import SESHandler

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class NotifHandler:

    def __init__(self):
        pass

    def send_emails(self, user_info, message):
        ses = SESHandler.get_instance()
        email_subject = EMAIL_SUBJECT % (message['capacity'], message['center_name'], str(message['pincode']))
        for info in user_info:
            email_body = EMAIL_BODY % (message['center_name'], message['district_name'], message['date'],
                                       message['age_group'], message['vaccine'], message['address'], message['pincode'],
                                       message['fee_type'], message['slots'], info[0], info[1])
            ses.send_email(os.getenv('SENDER_EMAIL'),[info[0]],email_subject,email_body)
        return

    def send_template_emails(self, user_info, message):
        ses = SESHandler.get_instance()
        for info in user_info:
            unsub_edpoint = UNSUB_ENDPOINT % (info[0], info[1])
            template_data = TEMPLATE_DATA % (message['center_name'], message['slots'], message['district_name'],
                                            message['date'], message['age_group'], message['vaccine'], message['address'],
                                            message['pincode'], unsub_edpoint, message['capacity'], message['capacity_dose_1'],
                                            message['capacity_dose_2'], message['fee_amount'])
            ses.send_template_email(os.getenv('SENDER_EMAIL'),[info[0]],template_data)
        return

    def send_verification_email(self, user_email, create_new_bool):
        ses = SESHandler.get_instance()
        db = DBHandler.get_instance()
        if create_new_bool is True:
            token = str(uuid.uuid4())
            db.insert(ADD_USER_TOKEN,(token, user_email))
        else:
            info = db.query(GET_USER_QUERY, (user_email,))
            token = info[0][2]
        body = VERIFY_EMAIL_BODY % (user_email, token)
        subject = VERIFY_SUBJECT
        ses.send_email(os.getenv('SENDER_EMAIL'), [user_email], subject, body)
        return