import psycopg2
from psycopg2.extras import RealDictCursor
import subprocess
from hmac import compare_digest
from time import sleep
from fastapi import FastAPI
import uvicorn
import os
import time


while True:
    try:
        conn = psycopg2.connect(dbname='preprints', user='postgres', host='database', password=os.environ['POSTGRES_PASSWORD'])
        break
    except psycopg2.OperationalError:
        print('trying to connect to database..')
        time.sleep(1)
cur = conn.cursor(cursor_factory=RealDictCursor)

KEYS = os.environ['KEYS'].split(',')
ELEVATED_KEYS = os.environ['ELEVATED_KEYS'].split(',')

app = FastAPI()


def is_authenticated(key, elevated):
    sleep(0.1)
    if elevated:
        return True in [compare_digest(key, valid_key) for valid_key in ELEVATED_KEYS]
    else:
        return True in [compare_digest(key, valid_key) for valid_key in KEYS]


def convert_row_to_json(row):
    row['report_generated_timestamp'] = row['report_generated_timestamp'].strftime('%Y-%m-%d %H:%M:%S')
    row['publication_date'] = row['publication_date'].strftime('%Y-%m-%d')
    row['release_status'] = {1: 'not posted', 2: 'placeholder annotation', 3: 'full annotation', 4: 'full annotation and tweeted'}[row['release_status']]
    return row


@app.get('/recent_reports')
def get_recent_reports(key: str, cursor: int):
    if not is_authenticated(key, False):
        return {'success': False, 'error': 'Authentication failed.'}
    cur.execute('select doi, release_status, report_generated_timestamp, html_report, url, title, authors, abstract, publication_date, annotation_link, jet_page_numbers, limitation_sentences, trial_numbers, sciscore, is_modeling_paper, graph_types, is_open_data, is_open_code from preprints where report_generated_timestamp is not null order by id desc limit %s offset %s', (50, cursor,))
    return [convert_row_to_json(dict(row)) for row in cur.fetchall()]


@app.post('/update')
def update_database(key: str):
    if not is_authenticated(key, True):
        return {'success': False, 'error': 'Authentication failed.'}
    subprocess.Popen(['python', '-u', 'update.py'])
    return {'success': True}


def generate_key():
    from secrets import token_hex
    return token_hex(20)


if __name__ == '__main__':
    uvicorn.run('server:app', host='0.0.0.0', port=80)