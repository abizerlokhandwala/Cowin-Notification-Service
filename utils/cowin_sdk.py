import requests

from utils.constants import STATES_URL, DISTRICTS_URL, CALENDAR_BY_DISTRICT_URL


class CowinAPI:

    def __init__(self):
        pass

    def get_states(self):
        headers = {'Content-Type': 'application/json', 'Connection': 'keep-alive', 'Date': 'Sun, 02 May 2021 12:13:52 GMT', 'x-amzn-RequestId': 'fa5cc99b-4bc6-4c58-a00b-7ae493899648', 'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token', 'x-amzn-ErrorType': 'ForbiddenException', 'x-amz-apigw-id': 'esycDEDOhcwFi5g=', 'Access-Control-Allow-Methods': 'DELETE,GET,HEAD,OPTIONS,PATCH,POST,PUT', 'X-Amzn-Trace-Id': 'Root=1-608e9780-55c40e7e2f0e25ee53a32e6b', 'X-Cache': 'Miss from cloudfront', 'Via': '1.1 795fca0399f361701665c0d9fab45325.cloudfront.net (CloudFront)', 'X-Amz-Cf-Pop': 'IAD79-C2', 'X-Amz-Cf-Id': 'kBgRI718LxUCpktvkH3zx_W2xeiie-o4YWDPfLQQXINwRGSVCFb0rA=='}
        response = requests.get(STATES_URL,headers=headers)
        print(response.__dict__)
        print(response.status_code)
        response = response.json()
        print(response)
        return response['states']

    def get_districts(self, state_id):
        response = requests.get(f'{DISTRICTS_URL}{state_id}')
        response = response.json()
        return response['districts']

    def get_centers(self, district_id, date):
        response = requests.get(f'{CALENDAR_BY_DISTRICT_URL}?district_id={district_id}&date={date}')
        response = response.json()
        return response['centers']
