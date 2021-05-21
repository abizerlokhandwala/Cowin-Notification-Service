import argparse
import json
import gzip
from geopy.geocoders import GoogleV3
import itertools
from geopy import distance

DISTANCE_CUTOFF = 100

parser = argparse.ArgumentParser(description='Generate PIN Code Proximity DB')
parser.add_argument('--apikey', required=True,
                    help='Google Maps API Key')
parser.add_argument('--pincodes', default='',
                    help='Path to JSON file containing all the PIN code data from data.gov.in')
parser.add_argument('--db', required=True,
                    help='Path of Output GZipped JSON file which will contain list of all PIN codes and their proximity data. Used as a cache to avoid unnecessary recalculation')
parser.add_argument('--centers', default='',
                    help='Path to JSON file containing list of Cowin centers whose PIN codes do not exist in data.gov.in Dataset')

args = parser.parse_args()

# setup geolocator
geolocator = GoogleV3(api_key=args.apikey)

# import pincodes json
try:
  with open(args.pincodes) as inputFile:
    dataset = json.load(inputFile)['data']
    print('Found PIN codes listing with', len(dataset), 'entries')
except FileNotFoundError:
  print('No Dataset found')
  dataset = []

# import extra pincodes json
try:
  with open(args.centers) as inputFile:
    centers = json.load(inputFile)
    print('Found extra Centers listing with', len(centers), 'centers')
except FileNotFoundError:
  print('No extra Centers found')
  centers = []

# look for existing db
try:
  with gzip.open(args.db, 'r') as fin:
    print('Loading existing DB, this may take a while...')
    db = json.loads(fin.read().decode('utf-8'))
except FileNotFoundError:
  print('No existing DB found, building from scratch')
  db = {}

pincodes = []
meta = {}
for entry in dataset:
  pincode = entry[4]
  if (not pincode) or (len(pincode) != 6):
    raise Exception('Invalid PIN Code: ' + pincode)
  if pincode in meta:
    meta[pincode].append(entry)
  else:
    meta[pincode] = [entry]
  pincodes.append(pincode)

for center in centers:
  pincode = str(center['pincode'])
  # 0 is a special case - Cowin returns a center with 0 pincode for some reason
  if pincode == '0':
    continue
  if (not pincode) or (len(pincode) != 6):
    raise Exception('Invalid PIN Code: ' + pincode)
  if pincode in meta:
    meta[pincode].append(center)
  else:
    meta[pincode] = [center]
  pincodes.append(pincode)

# get unique list of PIN codes
pincodes = set(pincodes)
print('Total', len(pincodes), 'unique PIN codes')

# get location for each new pincode
existingPincodes = set(db.keys())
newPincodes = []
unlocatedPincodes = []
for i, pincode in enumerate(pincodes):
  if not (pincode in existingPincodes):
    print(f"Locating PIN {pincode} ({str(i+1)}/{len(pincodes)})")

    location = geolocator.geocode(f'India {pincode}')
    if not location:
      print('Unable to locate PIN:', pincode, 'Skipping...')
      unlocatedPincodes.append(pincode)
      continue
    if (location.address == pincode):
      print(f'WARN: Unstructured Geo Lookup for PIN Code: {pincode} - {location.address}')
    elif not (location.address.endswith('India')):
      print('Non-India location for PIN:', pincode, 'Skipping...')
      unlocatedPincodes.append(pincode)
      continue

    newPincodes.append(pincode)

    db[pincode] = {
      'coordinates': {
        'latitude': location.latitude,
        'longitude': location.longitude,
      },
      'meta': meta[pincode]
    }

print('Located', len(newPincodes), 'new PIN codes')
print(len(unlocatedPincodes), 'new PIN codes could not be located and will be ignored')

# for each new pincode
for i, pincode in enumerate(newPincodes):
  print(f"Calculating distances for existing PIN codes to new PIN code {pincode} ({str(i+1)}/{len(newPincodes)})")
  location = (db[pincode]['coordinates']['latitude'],db[pincode]['coordinates']['longitude'])
  # calculate distance from all existing pincodes
  for existingPincode in existingPincodes:
    existingPincodeLocation = (db[existingPincode]['coordinates']['latitude'],db[existingPincode]['coordinates']['longitude'])
    dist = distance.great_circle(location, existingPincodeLocation).km
    if (dist >= DISTANCE_CUTOFF):
      continue

    # update proximity lists for both the new pincode and the existing pincode
    db[pincode].setdefault('proximity', []).append({ 'pincode': existingPincode, 'distance': dist })
    db[existingPincode].setdefault('proximity', []).append({ 'pincode': pincode, 'distance': dist })
  
# calculate distance from all new pincodes
combinations = list(itertools.combinations(newPincodes, 2))
for i, (newPincode1, newPincode2) in enumerate(combinations):
  print(f"Calculating distances between new PIN codes {newPincode1} - {newPincode2} ({str(i+1)}/{len(combinations)})")
  newPincode1Location = (db[newPincode1]['coordinates']['latitude'],db[newPincode1]['coordinates']['longitude'])
  newPincode2Location = (db[newPincode2]['coordinates']['latitude'],db[newPincode2]['coordinates']['longitude'])
  dist = distance.great_circle(newPincode1Location, newPincode2Location).km
  if (dist >= DISTANCE_CUTOFF):
    continue

  # update proximity lists for both the new pincodes
  db[newPincode1].setdefault('proximity', []).append({ 'pincode': newPincode2, 'distance': dist })
  db[newPincode2].setdefault('proximity', []).append({ 'pincode': newPincode1, 'distance': dist })

# sort all proximity lists
numDbItems = len(db.items())
print(f"Sorting proximity lists for all PIN codes...")
for i, (pincode,value) in enumerate(db.items()):
  if value.get('proximity'):
    value['proximity'] = sorted(value['proximity'], key=lambda k: k['distance'])

# write db to file
with gzip.open(args.db, 'w') as fout:
  print('Writing updated DB, this may take a while...')
  fout.write(json.dumps(db).encode('utf-8'))


