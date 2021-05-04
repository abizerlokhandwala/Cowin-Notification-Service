import os
import uuid

from helpers.constants import EMAIL_SUBJECT, EMAIL_BODY, VERIFY_EMAIL_BODY, VERIFY_SUBJECT
from helpers.db_handler import DBHandler
from helpers.queries import ADD_USER_TOKEN
from helpers.ses_handler import SESHandler


class NotifHandler:

    def __init__(self):
        pass

    def send_emails(self, user_emails, message):
        ses = SESHandler.get_instance()
        email_chunk = []
        email_subject = (EMAIL_SUBJECT % message['capacity'], message['center_name'])
        email_body = (EMAIL_BODY % (message['center_name'],message['district_name'],message['date'],
                                    message['age_group'],message['vaccine'],message['address'],message['pincode'],
                                    message['fee_type'],message['slots']))
        for email in user_emails:
            if len(email_chunk)<50:
                email_chunk.append(email)
            else:
                ses.send_email(os.getenv('SENDER_EMAIL'),email_chunk,email_subject,email_body)
                email_chunk = [email]
        if email_chunk:
            ses.send_email(os.getenv('SENDER_EMAIL'), email_chunk, email_subject, email_body)
        return

    def send_verification_email(self, user_email):
        ses = SESHandler.get_instance()
        token = str(uuid.uuid4())
        db = DBHandler.get_instance()
        db.insert(ADD_USER_TOKEN,(token, user_email))
        body = (VERIFY_EMAIL_BODY % user_email, token)
        subject = VERIFY_SUBJECT
        ses.send_email(os.getenv('SENDER_EMAIL'), user_email, subject, body)
        return