import gzip
import json
import os

import pymysql

with gzip.open('data/db.json.gz', 'r') as f:
    data = json.load(f)

values = []

for key, value in data.items():
    latitude = value['coordinates']['latitude']
    longitude = value['coordinates']['longitude']
    values.append(f"('{key}', {latitude}, {longitude})")

if __name__ == "__main__":
    INSERT_QUERY = f"INSERT INTO {os.getenv('DB_NAME')}.pincodes(pincode, latitude, longitude) VALUES " + \
                   (",".join(values)) + ";"
    connection = pymysql.connect(host=os.getenv('DB_HOSTNAME'), port=int(os.getenv('DB_PORT')),
                                 user=os.getenv('DB_USER'), password=os.getenv('DB_PASSWORD'))
    cursor = connection.cursor()
    cursor.execute(INSERT_QUERY)
    connection.commit()
    connection.close()
