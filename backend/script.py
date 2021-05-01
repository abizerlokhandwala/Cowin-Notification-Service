import requests

if __name__=="__main__":

    states = requests.get('https://cdn-api.co-vin.in/api/v2/admin/location/states')
    states = states.json()
    count = 0
    for state in states['states']:
        districts = requests.get(f'https://cdn-api.co-vin.in/api/v2/admin/location/districts/{state["state_id"]}')
        count += len(districts.json()['districts'])
        print(count)
    print(count)