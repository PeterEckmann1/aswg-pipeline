import shutil
import psycopg2
import requests
import json
import time
import os


POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')


def add_db_entry(doi, source, date, title, annotation_link, sciscore, limitation_recognizer, oddpub, barzooka, jetfighter):
    cur.execute('insert into Annotations (DOI, Source, Date, Title, AnnotationLink, SciScore, LimitationRecognizer, ODDPub, Barzooka, JetFighter) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', (doi, source, date, title, annotation_link, sciscore, limitation_recognizer, oddpub, barzooka, jetfighter))
    conn.commit()

def update_from_doi_list(file):
    with open(file, 'r') as f:
        for line in f:
            add_db_entry(line.replace('\n', ''), '', '', '', '', '', '', '', '', '')

def make_folder(id):
    print('Created folder', id)
    folder = '../papers/' + id
    if os.path.exists(folder):
        shutil.rmtree(folder)
    os.mkdir(folder)

def clear_db():
    print('Clearing database')
    cur.execute('drop table if exists Annotations')
    cur.execute('create table Annotations (DOI text, Source text, Date text, Title text, AnnotationLink text, SciScore text, LimitationRecognizer text, ODDPub text, Barzooka text, JetFighter text)')
    conn.commit()

def clear_papers():
    for f_name in os.listdir('../papers'):
        print('Deleted folder', f_name)
        shutil.rmtree('../papers/' + f_name)


clear_papers()
time.sleep(30)
conn = psycopg2.connect(dbname='postgres', user='postgres', password=POSTGRES_PASSWORD, host='annotation-db')
cur = conn.cursor()

cur.execute('create table if not exists Annotations (DOI text, Source text, Date text, Title text, AnnotationLink text, SciScore text, LimitationRecognizer text, ODDPub text, Barzooka text, JetFighter text)')
cur.execute('select * from annotations')
if len(cur.fetchall()) < 10:
    print(cur.fetchall())
    clear_db()
    update_from_doi_list('doi_list.csv')

cur.execute('select DOI from Annotations')
dois = [doi[0] for doi in cur.fetchall()]
collection = json.loads(requests.get('https://connect.biorxiv.org/relate/collection_json.php?grp=181').text)
for rel in reversed(collection['rels']):
    if rel['rel_doi'] not in dois:
        make_folder(rel['rel_doi'].split('10.1101/')[1])

cur.close()
conn.close()