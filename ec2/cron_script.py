import logging
import random
import string
import time
import boto3
import os

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

client = boto3.client('lambda', region_name='ap-south-1',
                      aws_access_key_id=os.getenv('aws_access_key'),
                      aws_secret_access_key=os.getenv('aws_secret_key')
                      )
TRIGGER_FUNCTION_NAME = 'cowin-notification-service-dev-trigger_district_updates'
UPDATE_FUNCTION_NAME = 'cowin-notification-service-dev-update_district_slots'

def random_str(length):
    res = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
    return str(res)

if __name__ == "__main__":
    while True:
        try:
            response = client.invoke(FunctionName=TRIGGER_FUNCTION_NAME,
                          InvocationType='Event',Payload='')
            var = client.get_function_configuration(FunctionName=UPDATE_FUNCTION_NAME)
            var['Environment']['Variables']['DUMMY'] = random_str(20)
            client.update_function_configuration(FunctionName=UPDATE_FUNCTION_NAME,
                                                 Environment=var['Environment'])
            time.sleep(10)
        except Exception as e:
            print(e)
            pass