import logging
import boto3
from botocore.exceptions import ClientError

class SESHandler:

    __instance = None

    def __init__(self):
        self.client = boto3.client('ses')
        SESHandler.__instance = self

    @staticmethod
    def get_instance():
        if SESHandler.__instance is None:
            SESHandler()
        return SESHandler.__instance

    def send_email(self, sender, recipients, subject, body_html):
        CHARSET = "UTF-8"
        response = self.client.send_email(
            Destination={
                'BccAddresses': recipients,
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': CHARSET,
                        'Data': body_html,
                    }
                },
                'Subject': {
                    'Charset': CHARSET,
                    'Data': subject,
                },
            },
            Source=sender,
        )
        try:
            pass
        except ClientError as e:
            logging.error(e.response['Error']['Message'])
            return False
        else:
            logging.info(f"Emails sent to {recipients}")
        return response