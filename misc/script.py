import requests
import time

if __name__=="__main__":
    start = time.time()
    states = requests.get('https://cdn-api.co-vin.in/api/v2/admin/location/states')
    states = states.json()
    count = 0
    for state in states['states']:
        districts = requests.get(f'https://cdn-api.co-vin.in/api/v2/admin/location/districts/{state["state_id"]}')
        districts = districts.json()
        for district in districts['districts']:
            days_data = requests.get(f'https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByDistrict?district_id={district["district_id"]}&date=2-05-2021')
        count += len(districts['districts'])
        print(count)
    print(count)
    done = time.time()
    elapsed = done - start
    print(elapsed)
    #Took 24min to get all districts all states