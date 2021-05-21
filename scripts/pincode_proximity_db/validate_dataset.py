# query for district list
import requests
import json
import os
dirname = os.path.dirname(__file__)
dataDir = os.path.join(dirname, 'data')
districtsFile = os.path.join(dataDir, 'districts.json')
centersFile = os.path.join(dataDir, 'centers.json')
dataGovPincodesFile = os.path.join(dataDir, 'pincodes_data.gov.in_15May2021.json')
geoNamesPincodesFile = os.path.join(dataDir, 'IN.txt')

HEADERS = {
  'accept': 'application/json',
  'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36'
}

DATE = '31-03-2021'

def listDistricts():
  r = requests.get('https://cdn-api.co-vin.in/api/v2/admin/location/states', headers=HEADERS)
  print('Listed States:', r.status_code)
  states = r.json()['states']

  districts = []
  for i, state in enumerate(states):
    r = requests.get('https://cdn-api.co-vin.in/api/v2/admin/location/districts/' + str(state['state_id']), headers=HEADERS)
    print(f"Listed Districts For State {state['state_name']} : {r.status_code} ({str(i+1)}/{str(len(states))})")
    districts.extend(r.json()['districts'])

  with open(districtsFile, 'w') as outfile:
    json.dump(districts, outfile)

def loadDistricts():
  with open(districtsFile) as inputFile:
    districts = json.load(inputFile)
  print('Found', len(districts), 'districts')
  return districts

def loadGeoNamesPinCodes():
  with open(geoNamesPincodesFile) as inputFile:
    input = inputFile.readlines()
  
  pinCodes = []
  for l in input:
    if not l.startswith('IN\t'):
      raise Exception('Malformed line', l)
    pinCode = l.split('\t')[1]
    if (not pinCode) or (len(pinCode) != 6):
      raise Exception('Invalid PIN Code: ' + pinCode)
    pinCodes.append(pinCode)

  pinCodes = set(pinCodes)
  print('Loaded', len(pinCodes), 'unique Secondary PIN codes')
  return pinCodes

def loadDataGovPinCodes():
  with open(dataGovPincodesFile) as inputFile:
    input = json.load(inputFile)

  print('Found PIN codes listing with', len(input['data']), 'entries')

  pinCodes = []
  for entry in input['data']:
    pinCode = entry[4]
    if (not pinCode) or (len(pinCode) != 6):
      raise Exception('Invalid PIN Code: ' + pinCode)
    pinCodes.append(pinCode)

  # get unique list of PIN codes
  pinCodes = set(pinCodes)
  print('Loaded', len(pinCodes), 'unique PIN codes')
  return pinCodes

def listCenters():
  districts = loadDistricts()
  # for each district, query for centers
  centers = []
  for i, district in enumerate(districts):
    r = requests.get('https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByDistrict?district_id=' + str(district['district_id']) + '&date=' + DATE, headers=HEADERS)
    print(f"Listed Centers For District {district['district_name']} : {r.status_code} ({str(i+1)}/{len(districts)})")
    centers.extend(r.json()['centers'])
  
  with open(centersFile, 'w') as outfile:
    json.dump(centers, outfile)

def loadCenters():
  with open(centersFile) as inputFile:
    centers = json.load(inputFile)
  print('Found', len(centers), 'centers')
  return centers

def listMissingPinCodes(centers, pinCodes, datasetName):
  # for each center, get the pinCode
  missingPinCodes = []
  centersMap = {}
  for center in centers:
    centerPinCode = str(center['pincode'])
    centersMap[centerPinCode] = center
    if not (centerPinCode in pinCodes):
      missingPinCodes.append(centerPinCode)

  # get unique list
  missingPinCodes = set(missingPinCodes)
  print('Missing', len(missingPinCodes), 'unique PIN codes in', datasetName)

  with open(os.path.join(dataDir, f'{datasetName}_missing.json'), 'w') as outfile:
    json.dump([centersMap[p] for p in missingPinCodes], outfile)

if __name__ == "__main__":
  # uncomment to refresh district list from Cowin
  # listDistricts()
  # uncomment to refresh center list from Cowin
  # listCenters()

  dataGovPinCodes = loadDataGovPinCodes()
  geoNamesPinCodes = loadGeoNamesPinCodes()
  
  centers = loadCenters()
  listMissingPinCodes(centers, dataGovPinCodes, 'data_gov')
  listMissingPinCodes(centers, geoNamesPinCodes, 'geo_names')



