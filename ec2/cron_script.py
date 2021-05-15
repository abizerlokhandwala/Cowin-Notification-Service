import logging
import random
import string
import time
import boto3
import os
from datetime import datetime, time as datetime_time
import pytz #for conversion of UTC to IST

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

client = boto3.client('lambda', region_name='ap-south-1',
                      aws_access_key_id=os.getenv('aws_access_key'),
                      aws_secret_access_key=os.getenv('aws_secret_key')
                      )
TRIGGER_FUNCTION_NAME = 'cowin-notification-service-dev-trigger_district_updates'
UPDATE_FUNCTION_NAME = 'cowin-notification-service-dev-update_district_slots'

TIME_SLEEP_FROM = datetime_time(1,00)
TIME_TILL_ASLEEP = datetime_time(5,30)

def random_str(length):
    res = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
    return str(res)

# Checking if time is between a specific range
# https://stackoverflow.com/questions/10048249/how-do-i-determine-if-current-time-is-within-a-specified-range-using-pythons-da
# https://www.geeksforgeeks.org/get-current-time-in-different-timezone-using-python/
def is_time_between(begin_time, end_time, check_time=None):
    IST = pytz.timezone('Asia/Kolkata')
    # If check time is not given, default to current IST time
    check_time = check_time or datetime.now(IST).time()
    if begin_time < end_time:
        return begin_time <= check_time <= end_time
    else: # crosses midnight
        return check_time >= begin_time or check_time <= end_time

if __name__ == "__main__":
    while True:
        try:
            if not is_time_between(TIME_SLEEP_FROM, TIME_TILL_ASLEEP):
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