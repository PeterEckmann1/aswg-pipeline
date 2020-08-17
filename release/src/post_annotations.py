import os
import time
import hypothesis
import requests
import shutil
import random
from requests_oauthlib import OAuth1Session
from urllib.parse import quote
import psycopg2
import datetime


REQUESTS_HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:64.0) Gecko/20100101 Firefox/64.0'}

HYPOTHESIS_USER = os.getenv('HYPOTHESIS_USER')
HYPOTHESIS_TOKEN = os.getenv('HYPOTHESIS_TOKEN')

POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')

TWITTER_CLIENT_KEY = os.getenv('TWITTER_CLIENT_KEY')
TWITTER_CLIENT_SECRET = os.getenv('TWITTER_CLIENT_SECRET')
TWITTER_OWNER_KEY = os.getenv('TWITTER_OWNER_KEY')
TWITTER_OWNER_SECRET = os.getenv('TWITTER_OWNER_SECRET')

h = hypothesis.Hypothesis(username=HYPOTHESIS_USER, token=HYPOTHESIS_TOKEN)

def send_tweet(text):
    session = OAuth1Session(TWITTER_CLIENT_KEY, TWITTER_CLIENT_SECRET, TWITTER_OWNER_KEY, TWITTER_OWNER_SECRET)
    url = 'https://api.twitter.com/1.1/statuses/update.json?status=' + quote(text, safe='')
    r = session.post(url)
    if r.status_code == 403:
        print('Tweet not sent:', text)

def post_hypothesis_annotation(body, doi, url):
    payload = {
        'uri': url,
        'text': body,
        'document': {'title': [url], 'highwire': {'doi': [doi]}},
        'permissions': h.permissions,
        'group': h.group}
    r = h.post_annotation(payload)
    return r.json()['links']['incontext']

def get_annotation_for_tool(tool, id):
    with open('../papers/{}/{}.html'.format(id, tool), 'r', encoding='utf-8') as f:
        return f.read()

def get_db_for_tool(tool, id):
    with open('../papers/{}/{}_db.txt'.format(id, tool), 'r', encoding='utf-8') as f:
        return f.read()

def get_url(doi):
    med_url = 'http://medrxiv.org/cgi/content/short/' + doi.split('10.1101/')[1]
    bio_url = 'http://biorxiv.org/cgi/content/short/' + doi.split('10.1101/')[1]
    if requests.get(med_url).status_code == 404:
        url = bio_url
    else:
        url = med_url
    return url

def get_title(url):
    html = requests.get(url, headers=REQUESTS_HEADERS).text
    for line in html.split('\n'):
        if '<meta name="DC.Title"' in line:
            return line.split('<meta name="DC.Title" content="')[1].split('"')[0]

def add_db_entry(doi, source, date, title, annotation_link, sciscore, limitation_recognizer, oddpub, barzooka, jetfighter):
    cur.execute('insert into Annotations (DOI, Source, Date, Title, AnnotationLink, SciScore, LimitationRecognizer, ODDPub, Barzooka, JetFighter) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', (doi, source, date, title, annotation_link, sciscore, limitation_recognizer, oddpub, barzooka, jetfighter))
    conn.commit()

def add_data_log(data):
    data_file = open('../performance-data/data.csv', 'a')
    data_file.write(data)
    data_file.close()


time.sleep(30)
conn = psycopg2.connect(dbname='postgres', user='postgres', password=POSTGRES_PASSWORD, host='annotation-db')
cur = conn.cursor()

open('../performance-data/data.csv', 'w').close()
permanent = 0

tools = ['sciscore', 'limitation-recognizer', 'oddpub', 'barzooka', 'jetfighter']
while True:
    time.sleep(random.random())
    ids = os.listdir('../papers')
    print('Number of papers left:', len(ids))
    sums = [0, 0, 0, 0, 0]
    for id in ids:
        if not os.path.exists('../papers/' + id + '/release_started'):
            files = os.listdir('../papers/' + id)
            for i, tool in enumerate(tools):
                if tool + '.html' in files:
                    sums[i] += 1
            if not False in [tool + '.html' in files for tool in tools]:
                open('../papers/' + id + '/release_started', 'w').close()
                print('Started processing', id)
                sciscore = get_annotation_for_tool('sciscore', id)
                limitation_recognizer = get_annotation_for_tool('limitation-recognizer', id)
                oddpub = get_annotation_for_tool('oddpub', id)
                barzooka = get_annotation_for_tool('barzooka', id)
                jetfighter = get_annotation_for_tool('jetfighter', id)

                body = sciscore.replace('<p><b>About SciScore</b></p>', '<hr>{}<hr><p><b>About SciScore</b></p>'.format('<hr style="border-top: 1px solid #ccc;">'.join([oddpub, limitation_recognizer, barzooka, jetfighter])))
                doi = '10.1101/' + id
                url = get_url(doi)
                body = body.replace('\n', ' ').replace('  ',' ')

                anno_link = post_hypothesis_annotation(body, doi, url)

                title = get_title(url)

                add_db_entry(doi, 'pdf', str(datetime.date.today()), title, anno_link, get_db_for_tool('sciscore', id), get_db_for_tool('limitation-recognizer', id), get_db_for_tool('oddpub', id), get_db_for_tool('barzooka', id), get_db_for_tool('jetfighter', id))

                if len(title) > 50:
                    title = title[:50].rstrip() + '...'

                total_rigor = body.count('<td style="min-width:100px;margin-right:1em; border-right:1px solid lightgray; border-bottom:1px solid lightgray">')
                addressed_rigor = total_rigor - body.count('<td style="min-width:100px;border-bottom:1px solid lightgray">not detected.</td>')
                resource_count = body.count('<div style="margin-bottom:8px">')
                shutil.rmtree('../papers/' + id)
                permanent += 1
                sums = [val - 1 for val in sums]

                if '<i>NIH rigor criteria are not applicable to paper type.</i>' in body:
                    tweet = 'The paper “{}” ({}) has been reviewed by a set of automated tools; find the results of the analysis here: {}. We detected {} key resource{}.'.format(title, url, anno_link, resource_count, '' if resource_count == 1 else 's')
                else:
                    tweet = 'The paper “{}” ({}) has been reviewed by a set of automated tools; find the results of the analysis here: {}. We detected {} of {} rigor criteria and {} key resource{}.'.format(title, url, anno_link, addressed_rigor, total_rigor, resource_count, '' if resource_count == 1 else 's')

                send_tweet(tweet)
                print('Tweet sent for', anno_link)

    add_data_log(','.join([str(sum + permanent) for sum in sums]) + '\n')