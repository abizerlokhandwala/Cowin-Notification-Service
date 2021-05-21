## Pincode Proximity DB

To generate, run the script like:

```bash
python scripts/pincode_proximity_db/generate.py --pincodes scripts/pincode_proximity_db/data/pincodes.json --apikey xyz123 --db scripts/pincode_proximity_db/data/db.json.gz --centers scripts/pincode_proximity_db/data/extra_pincodes.json
```

It does the following:

1. Reads pincodes from data.gov.in file (Obtained from https://data.gov.in/node/6818285)
2. Reads pincodes from `extrapincodes` file
2. For each pincode, it fetches the Lat/Long coordinates using google maps API
3. It builds a distance matrix using Haversine distance calculation for all pincodes
4. Outputs the database as a gzipped json object of the form:

```json
{
  "411010": {
    "proximity": [
      { "pincode": "411011", "distance": 0.24 },
      { "pincode": "411012", "distance": 0.67 },
      { "pincode": "411020", "distance": 1.56 },
      # a list of pincodes by increasing order of distance, until a cut-off distance (defaults to 100km)
    ],
    "coordinates": {
      "latitude":  <>,
      "longitude": <>,
    },
    "meta": [{source1}, {source2}] # sources are objects in the data.gov dataset or cowin centre listing that referenced the PIN
}
```

The script checks if the database file exists and if found, uses it as a cache. It only performs lat/long lookup and distance calculations when required