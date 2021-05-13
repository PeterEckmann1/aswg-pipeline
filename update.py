import psycopg2
import json
from report import get_reports
from utils.release.hypothesis import Hypothesis
import subprocess
import os
import pickle
from bs4 import BeautifulSoup
from datetime import date
import release
import re
from tqdm import tqdm


def get_urls(urls):
    pickle.dump(urls, open('urls.pickle', 'wb'))
    subprocess.call(['python', 'get_urls.py'])
    output = pickle.load(open('url_responses.pickle', 'rb'))
    os.remove('url_responses.pickle')
    os.remove('urls.pickle')
    return output


def get_dois(pages):
    return [[rel['rel_doi'] for rel in r.json()['collection']] for r in get_urls([f'https://api.biorxiv.org/covid19/{page}/json' for page in pages])]


def get_metadata_from_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    metadata = {'title': '', 'abstract': '', 'authors': [], 'publication_date': None}
    for meta in soup.findAll('meta'):
        if meta.get('name') == 'DC.Title':
            metadata['title'] = BeautifulSoup(meta.get('content'), 'html.parser').get_text()
        if meta.get('name') == 'DC.Description':
            metadata['abstract'] = BeautifulSoup(meta.get('content'), 'html.parser').get_text().split('\n\n###')[0].strip()
        if meta.get('name') == 'DC.Date':
            metadata['publication_date'] = date(*[int(num) for num in meta.get('content').split('-')])
        if meta.get('name') == 'citation_author':
            metadata['authors'].append(BeautifulSoup(meta.get('content'), 'html.parser').get_text())
    metadata['is_full_text_html'] = 'data-panel-name="article_tab_full_text' in html
    return metadata


def get_metadata(dois):
    medrxiv_rs = get_urls(['https://medrxiv.org/cgi/content/' + doi for doi in dois])
    is_medrxiv = []
    biorxiv_urls = []
    for i, r in enumerate(medrxiv_rs):
        is_medrxiv.append(r.status_code != 404)
        if r.status_code == 404:
            biorxiv_urls.append('https://biorxiv.org/cgi/content/' + dois[i])
    biorxiv_rs = get_urls(biorxiv_urls)
    biorxiv_i = 0
    result = []
    for i, doi in enumerate(dois):
        if is_medrxiv[i]:
            metadata = get_metadata_from_html(medrxiv_rs[i].text)
            result.append({'url': 'https://medrxiv.org/cgi/content/' + doi, 'has_full_text_html': metadata['is_full_text_html'], 'title': metadata['title'], 'abstract': metadata['abstract'], 'authors': metadata['authors'], 'publication_date': metadata['publication_date']})
        else:
            metadata = get_metadata_from_html(biorxiv_rs[biorxiv_i].text)
            result.append({'url': 'https://biorxiv.org/cgi/content/' + doi, 'has_full_text_html': metadata['is_full_text_html'], 'title': metadata['title'], 'abstract': metadata['abstract'], 'authors': metadata['authors'], 'publication_date': metadata['publication_date']})
            biorxiv_i += 1
    return result


def update_preprint_list(dois=None):     #todo can cache retrieved pages
    if dois is None:
        i = 0
        doi_lists = []
        dois = []
        while not doi_lists or doi_lists[-1] != []:
            doi_lists = get_dois(range(i, i + 2400, 30))
            for doi_list in doi_lists:
                dois = dois + doi_list
            i += 2400
    for i, doi in enumerate(dois):
        cur.execute('select doi from preprints where doi = %s', (doi,))
        if not cur.fetchone():
            cur.execute('insert into preprints (doi, report_exists, release_status) values (%s, false, 1)', (doi,))
    conn.commit()


def update_metadata():
    cur.execute('select doi from preprints where has_full_text_html is null or not has_full_text_html')
    dois = []
    for row in cur:
        dois.append(row[0])
    metadata = get_metadata(dois)
    for i, doi in enumerate(dois):
        cur.execute('update preprints set url = %s, has_full_text_html = %s , title = %s, abstract = %s, authors = %s, publication_date = %s where doi = %s', (metadata[i]['url'], metadata[i]['has_full_text_html'], metadata[i]['title'], metadata[i]['abstract'], json.dumps(metadata[i]['authors']), metadata[i]['publication_date'], doi))
    conn.commit()


def update_annotations():
    cur.execute('select doi, url, html_report, annotation_link from preprints where (release_status = 1 or release_status = 2) and report_exists')
    rows = cur.fetchall()
    for doi, url, html_report, annotation_link in tqdm(rows, desc='updating annotations'):
        if annotation_link:
            annotation = hypothesis.get_annotation(annotation_link.split('https://hyp.is/')[1].split('/')[0])
            hypothesis.update_annotation(annotation_link.split('https://hyp.is/')[1].split('/')[0],
                                         {'uri': annotation['uri'],
                                          'text': html_report,
                                          'document': annotation['document'],
                                          'permissions': annotation['permissions'],
                                          'group': annotation['group']})
        else:
            annotation_link = hypothesis.post_annotation({'uri': url.replace('https://', 'https://www.'),
                                                          'text': html_report,
                                                          'document': {'title': [url], 'highwire': {'doi': [doi]}},
                                                          'permissions': hypothesis.permissions,
                                                          'group': hypothesis.group}).json()['links']['incontext']
        cur.execute('update preprints set annotation_link = %s, release_status = 3 where doi = %s', (annotation_link, doi))
        conn.commit()

    # cur.execute('select doi, url from preprints where release_status = 1')
    # rows = cur.fetchall()
    # for doi, url in rows:
    #    annotation_link = hypothesis.post_annotation({'uri': url.replace('https://', 'https://www.'),
    #                                                  'text': 'Report will be posted here in 24-48 hours.',
    #                                                  'document': {'title': [url], 'highwire': {'doi': [doi]}},
    #                                                  'permissions': hypothesis.permissions,
    #                                                  'group': hypothesis.group}).json()['links']['incontext']
    #    cur.execute('update preprints set annotation_link = %s, release_status = 2 where doi = %s', (annotation_link, doi))
    #    conn.commit()


def update_tweets():
    cur.execute('select doi, tweet_text, annotation_link from preprints where release_status = 3 order by publication_date desc')
    rows = cur.fetchall()
    for doi, tweet_text, annotation_link in tqdm(rows, desc='updating tweets'):
        tweet_text_with_link = tweet_text.format(annotation_link)
        for i in range(9):
            try:
                release.update_twitter_status(tweet_text_with_link)
                break
            except Exception:
                tweet_text_with_link = re.sub('.{5}(?=…?”)', '', tweet_text_with_link)
        else:
            raise Exception('tweet could not be sent', tweet_text_with_link)
        cur.execute('update preprints set release_status = 4, tweet_text = %s where doi = %s', (tweet_text_with_link, doi))
        conn.commit()


def update_reports(allow_pdfs):     #todo eventually update reports which now have full text htmls available, because data isn't perfectly consistent now
    cur.execute('select doi from preprints where not report_exists' + ('' if allow_pdfs else ' and has_full_text_html'))
    dois = []
    for row in cur:
        if not dois or len(dois[-1]) > 100:
            dois.append([])
        dois[-1].append(row[0])
    print(sum([len(doi_set) for doi_set in dois]), 'remaining')
    for doi_set in dois:
        reports = get_reports(doi_set)
        for doi in reports:
            cur.execute('update preprints set report_exists = true, report_generated_timestamp = current_timestamp, html_report = %s, tweet_text = %s, discussion_text = %s, methods_text = %s, all_text = %s, jet_page_numbers = %s, limitation_sentences = %s, trial_numbers = %s, sciscore = %s, is_modeling_paper = %s, graph_types = %s, is_open_data = %s, is_open_code = %s, reference_check = %s, coi_statement = %s, funding_statement = %s, registration_statement = %s where doi = %s',
                        (reports[doi]['html_report'], reports[doi]['tweet_text'], reports[doi]['discussion_text'], reports[doi]['methods_text'], reports[doi]['all_text'], json.dumps(reports[doi]['jet_page_numbers']), json.dumps(reports[doi]['limitation_sentences']), json.dumps(reports[doi]['trial_numbers']), json.dumps(reports[doi]['sciscore']), reports[doi]['is_modeling_paper'], json.dumps(reports[doi]['graph_types']), reports[doi]['is_open_data'], reports[doi]['is_open_code'], json.dumps(reports[doi]['reference_check']), reports[doi]['coi_statement'], reports[doi]['funding_statement'], reports[doi]['registration_statement'], doi))
        conn.commit()


if __name__ == '__main__':
    import time
    hypothesis = Hypothesis(username=os.environ['HYPOTHESIS_USER'], token=os.environ['HYPOTHESIS_TOKEN'], group=os.environ['HYPOTHESIS_GROUP'])
    while True:
        try:
            # if running outside docker
            conn = psycopg2.connect(dbname='preprints', port=5433, user='postgres', host='localhost', password=os.environ['POSTGRES_PASSWORD'])
            cur = conn.cursor()
            break
        except psycopg2.DatabaseError:
            try:
                # if running inside docker
                conn = psycopg2.connect(dbname='preprints', port=5432, user='postgres', host='database', password=os.environ['POSTGRES_PASSWORD'])
                cur = conn.cursor()
                break
            except psycopg2.DatabaseError:
                time.sleep(1)
                pass

    print('updating preprint list')
    update_preprint_list()
    print('updating metadata')
    update_metadata()
    print('updating reports')
    update_reports(False)
    print('updating annotations')
    update_annotations()
    print('updating tweets')
    update_tweets()
