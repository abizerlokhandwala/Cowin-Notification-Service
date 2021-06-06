import json
import logging
import boto3
from botocore.exceptions import ClientError

from helpers.constants import TEMPLATE_DATA

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

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
        try:
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
        except ClientError as e:
            logger.error(e.response['Error']['Message'])
            return False
        return response

    def send_template_email(self, sender, recipients, template_data):
        try:
            response = self.client.send_templated_email(
                Destination={
                    'ToAddresses': recipients
                },
                Source=sender,
                Template='vaccinepostnew',
                TemplateData=template_data
            )
        except Exception as e:
            print(e)
            logger.error(e,exc_info=True)
            return False
        return response