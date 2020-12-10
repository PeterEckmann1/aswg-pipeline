import psycopg2
import json
from report import get_report
from utils.release.hypothesis import Hypothesis
import subprocess
import os
import pickle
from bs4 import BeautifulSoup
from datetime import date
import release


#normally false, only true when first populating db
check_old_reports = False


def get_urls(urls):
    pickle.dump(urls, open('urls.pickle', 'wb'))
    subprocess.call(['python', 'get_urls.py'])
    output = pickle.load(open('url_responses.pickle', 'rb'))
    os.remove('url_responses.pickle')
    os.remove('urls.pickle')
    return output


def get_dois(pages):
    return [[rel['rel_doi'] for rel in r.json()['collection']] for r in get_urls([f'https://api.biorxiv.org/covid19/{page}/json' for page in pages])]


def is_tweeted(dois):
    return ['@SciscoreReports' in r.text for r in get_urls(['https://connect.medrxiv.org/blog_get_tweets_blogs_mx.php?doi=' + doi for doi in dois])]


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


def update_preprint_list():
    i = 0
    doi_lists = []
    dois = []
    while not doi_lists or doi_lists[-1] != []:
        doi_lists = get_dois(range(i, i + 2400, 30))
        for doi_list in doi_lists:
            dois = dois + doi_list
        i += 2400
    if check_old_reports:
        already_existed = is_tweeted(dois)
    else:
        already_existed = [False for _ in dois]

    for i, doi in enumerate(dois):
        cur.execute('select doi from preprints where doi = %s', (doi,))
        if not cur.fetchone():
            cur.execute('insert into preprints (doi, report_exists, report_already_existed, release_status) values (%s, %s, %s, 1)', (doi, already_existed[i], already_existed[i]))
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
    cur.execute('select doi, url, html_report, annotation_link from preprints where (release_status = 1 or release_status = 2) and not report_already_existed and report_exists')
    rows = cur.fetchall()
    for doi, url, html_report, annotation_link in rows:
        if annotation_link:
            hypothesis.update_annotation(annotation_link.split('https://hyp.is/')[1].split('/')[0],
                                         {'uri': url.replace('https://', 'https://www.'),
                                          'text': html_report,
                                          'document': {'title': [url], 'highwire': {'doi': [doi]}},
                                          'permissions': hypothesis.permissions,
                                          'group': hypothesis.group})
        else:
            annotation_link = hypothesis.post_annotation({'uri': url.replace('https://', 'https://www.'),
                                                          'text': html_report,
                                                          'document': {'title': [url], 'highwire': {'doi': [doi]}},
                                                          'permissions': hypothesis.permissions,
                                                          'group': hypothesis.group}).json()['links']['incontext']
        cur.execute('update preprints set annotation_link = %s, release_status = 3 where doi = %s', (annotation_link, doi))

    cur.execute('select doi, url from preprints where release_status = 1 and not report_already_existed')
    rows = cur.fetchall()
    for doi, url in rows:
        annotation_link = hypothesis.post_annotation({'uri': url.replace('https://', 'https://www.'),
                                                      'text': 'Report will be posted here in 24-48 hours.',
                                                      'document': {'title': [url], 'highwire': {'doi': [doi]}},
                                                      'permissions': hypothesis.permissions,
                                                      'group': hypothesis.group}).json()['links']['incontext']
        cur.execute('update preprints set annotation_link = %s, release_status = 2 where doi = %s', (annotation_link, doi))
        break
    conn.commit()


def update_tweets():
    cur.execute('select doi, tweet_text, annotation_link from preprints where release_status = 3')
    rows = cur.fetchall()
    for doi, tweet_text, annotation_link in rows:
        tweet_text_with_link = tweet_text.format(annotation_link)
        release.update_twitter_status(tweet_text_with_link)
        cur.execute('update preprints set release_status = 4, tweet_text = %s where doi = %s', (tweet_text_with_link, doi))
        break
    conn.commit()


def update_reports():
    cur.execute('select doi from preprints where has_full_text_html and not report_exists')
    dois = []
    for row in cur:
        if not dois or len(dois[-1]) > 50:
            dois.append([])
        dois[-1].append(row[0])
    for doi_set in dois:
        reports = get_report(doi_set)
        for doi in reports:
            cur.execute('update preprints set report_exists = true, report_generated = current_timestamp, html_report = %s, tweet_text = %s, discussion_text = %s, methods_text = %s, all_text = %s, jet_page_numbers = %s, limitation_sentences = %s, trial_numbers = %s, sciscore = %s, is_modeling_paper = %s, graph_types = %s, is_open_data = %s, is_open_code = %s where doi = %s',
                        (reports[doi]['html_report'], reports[doi]['tweet_text'], reports[doi]['discussion_text'], reports[doi]['methods_text'], reports[doi]['all_text'], json.dumps(reports[doi]['jet_page_numbers']), json.dumps(reports[doi]['limitation_sentences']), json.dumps(reports[doi]['trial_numbers']), json.dumps(reports[doi]['sciscore']), reports[doi]['is_modeling_paper'], json.dumps(reports[doi]['graph_types']), reports[doi]['is_open_data'], reports[doi]['is_open_code'], doi))
    conn.commit()


if __name__ == '__main__':
    conn = psycopg2.connect(dbname='preprints', user='postgres', password=os.environ['POSTGRES_PASSWORD'])
    cur = conn.cursor()
    hypothesis = Hypothesis(username=os.environ['HYPOTHESIS_USER'], token=os.environ['HYPOTHESIS_TOKEN'],
                            group=os.environ['HYPOTHESIS_GROUP'])
    print('updating preprint list')
    update_preprint_list()
    print('updating metadata')
    update_metadata()
    print('updating reports')
    update_reports()
    #print('updating annotations')
    #update_annotations()
    #print('updating tweets')
    #update_tweets()
else:
    conn = psycopg2.connect(dbname='preprints', user='postgres', password=os.environ['POSTGRES_PASSWORD'])
    cur = conn.cursor()
    hypothesis = Hypothesis(username=os.environ['HYPOTHESIS_USER'], token=os.environ['HYPOTHESIS_TOKEN'],
                            group=os.environ['HYPOTHESIS_GROUP'])
    print('testing')