import subprocess
import psycopg2
import os


os.chdir('../')


subprocess.call('docker run --name test-database -e POSTGRES_PASSWORD=test -p 5432:5432 -d postgres')
conn = psycopg2.connect(dbname='postgres', user='postgres', host='test-database', password='test')
cur = conn.cursor()

cur.execute(open('generate_table.sql', 'r').read())