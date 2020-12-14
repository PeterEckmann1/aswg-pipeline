import subprocess
import psycopg2
import os
import time
import update


def get_dois(pages):
    print(pages)
    if pages[0] == 0:
        return [['10.1101/2020.12.09.417485']]
    else:
        return [[]]


os.chdir('../')


#subprocess.call('docker run --rm -e POSTGRES_PASSWORD=test -p 5433:5432 -d postgres')

while True:
    try:
        conn = psycopg2.connect(dbname='postgres', user='postgres', port='5433', password='test')
        break
    except psycopg2.OperationalError:
        time.sleep(1)
cur = conn.cursor()

#cur.execute(open('generate_table.sql', 'r').read())

#conn.commit()

update.get_dois = get_dois

update.update_preprint_list()