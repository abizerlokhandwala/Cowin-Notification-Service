import csv
import os

import pymysql

if __name__ == "__main__":
    connection = pymysql.connect(
        host=os.getenv('DB_HOSTNAME'),
        port=int(os.getenv('DB_PORT')),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'))

    cursor = connection.cursor()

    with open('districts.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                print(f'Column names are {", ".join(row)}')
                line_count += 1
            else:
                cursor.execute(f"INSERT INTO {os.getenv('DB_NAME')}.states_districts (state_id, state_name, district_id, district_name) "
                               f"values ('{row[0]}','{row[1]}','{row[2]}','{row[3]}')")
    connection.commit()