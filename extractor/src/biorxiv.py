import requests
from bs4 import BeautifulSoup
import string
import time


REQUESTS_HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:64.0) Gecko/20100101 Firefox/64.0'}
METHODS_HEADERS = ['METHOD',
                   'METHODS',
                   'MATERIALSANDMETHODS',
                   'MATERIALANDMETHOD',
                   'MATERIALANDMETHODS',
                   'MATERIALSANDMETHOD',
                   'METHODSANDMATERIALS',
                   'METHODANDMATERIALS',
                   'METHODSANDMATERIAL',
                   'METHODSANDMATERIAL'
                   'PROCEDURE',
                   'EXPERIMENTALPROCEDURE',
                   'EXPERIMENTALPROCEDURES',
                   'STUDYDESIGN',
                   'MATERIALSMETHODS',
                   'MATERIALMETHOD',
                   'MATERIALMETHODS',
                   'MATERIALSMETHOD',
                   'METHODSMATERIALS',
                   'METHODMATERIALS',
                   'METHODSMATERIAL',
                   'METHODSMATERIAL']


class Paper:
    def __init__(self, doi):
        self.doi = doi
        med_url = 'http://medrxiv.org/cgi/content/short/' + doi.split('10.1101/')[1]
        bio_url = 'http://biorxiv.org/cgi/content/short/' + doi.split('10.1101/')[1]
        try:
            if requests.get(med_url).status_code == 404:
                self.url = bio_url
            else:
                self.url = med_url
        except:
            time.sleep(10)
            if requests.get(med_url).status_code == 404:
                self.url = bio_url
            else:
                self.url = med_url

    def get_text(self):
        html = requests.get(self.url + '.full', headers=REQUESTS_HEADERS).text
        if 'data-panel-name="article_tab_full_text"' not in html:
            return None
        paper = []
        soup = BeautifulSoup(html, 'html.parser')
        for header in soup.find_all('h2')[:-2]:
            paper.append({'type': 'header', 'text': header.text})
            for tag in header.parent:
                if tag.name == 'p':
                    paper.append({'type': 'body', 'text': tag.text})
                if tag.name == 'div' and 'subsection' in tag['class']:
                    for subtag in tag:
                        if subtag.name == 'h3':
                            paper.append({'type': 'subheader', 'text': subtag.text})
                        if subtag.name == 'p':
                            paper.append({'type': 'body', 'text': subtag.text})
        return paper

    def get_methods(self):
        html = requests.get(self.url + '.full', headers=REQUESTS_HEADERS).text
        if 'data-panel-name="article_tab_full_text"' not in html:
            return None
        methods = ''
        soup = BeautifulSoup(html, 'html.parser')
        for header in soup.find_all('h2')[:-2]:
            if ''.join([letter for letter in header.text.upper() if letter in string.ascii_uppercase]) in METHODS_HEADERS:
                for tag in header.parent:
                    if tag.name == 'p':
                        methods += tag.text + ' '
                    if tag.name == 'div' and 'subsection' in tag['class']:
                        for subtag in tag:
                            methods += subtag.text + ' '
        return methods

    def save_pdf(self, file):
        try:
            r = requests.get(self.url + '.full.pdf', headers=REQUESTS_HEADERS)
        except:
            time.sleep(10)
            r = requests.get(self.url + '.full.pdf', headers=REQUESTS_HEADERS)
        with open(file, 'wb') as f:
            f.write(r.content)

    def get_metadata(self):
        html = requests.get(self.url, headers=REQUESTS_HEADERS).text
        names = []
        for line in html.split('\n'):
            if '<span class="nlm-surname">' in line:
                for name in line.split('<span class="nlm-surname">')[1:]:
                    names.append(name.split('<')[0])
                break
        title = ''
        for line in html.split('\n'):
            if '<meta name="DC.Title"' in line:
                title = line.split('<meta name="DC.Title" content="')[1].split('"')[0]
                break
        abstract = ''
        for line in html.split('\n'):
            if '<meta name="DC.Description"' in line:
                abstract = line.split('<meta name="DC.Description" content="')[1]
                break
        return {'names': names, 'title': title, 'abstract': abstract}


def get_dois(start, stop):
    dois = []
    for i in range(start, stop):
        html = requests.get('https://www.biorxiv.org/content/early/recent?page=' + str(i), headers=REQUESTS_HEADERS).text
        for line in html.split('\n'):
            if '<span class="highwire-cite-title">' in line:
                dois.append(line.split('/content/')[1].split('v')[0])
    return dois
