import os
import time
import boto3
import os

client = boto3.client('lambda', region_name='ap-south-1',
                      aws_access_key_id=os.getenv('aws_access_key'),
                      aws_secret_access_key=os.getenv('aws_secret_key')
                      )

if __name__ == "__main__":
    while True:

        response = client.invoke(FunctionName="cowin-notification-service-dev-trigger_district_updates",
                      InvocationType='Event',Payload='')
        time.sleep(10)