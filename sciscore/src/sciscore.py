import requests
from zipfile import ZipFile
import os
import json
import time


_USER_ID = os.getenv('SCISCORE_USER_ID')
_USER_TYPE = os.getenv('SCISCORE_USER_TYPE')
_API_KEY = os.getenv('SCISCORE_API_KEY')
_URL = os.getenv('SCISCORE_URL')


class Paper:
    def __init__(self, methods, id):
        self._methods = methods
        self._id = id.replace('/', '_')

    def download_report(self, file):
        params = {'userId': _USER_ID,
                  'userType': _USER_TYPE,
                  'documentId': self._id,
                  'sectionContent': self._methods,
                  'apiKey': _API_KEY,
                  'jsonOutput': 'true'}
        zip_file = file + '.zip'
        r = requests.post(url=_URL, data=params, timeout=305)
        if r.status_code != 200:
            print('Using blank SciScore, body text may not work.')
            params = {'userId': _USER_ID,
                      'userType': _USER_TYPE,
                      'documentId': 'test',
                      'sectionContent': 'test',
                      'apiKey': _API_KEY,
                      'jsonOutput': 'true'}
            r = requests.post(url=_URL, data=params, timeout=305)
            if r.status_code != 200:
                print('SciScore down')
                exit(0)
        with open(zip_file, 'wb') as f:
            f.write(r.content)
        with ZipFile(zip_file) as f:
            f.extractall(file)
        for f_name in os.listdir(file):
            if 'star_table' in f_name:
                os.remove(file + '/' + f_name)
        os.remove(zip_file)
        self._fix_whitespace(file)

    def _fix_whitespace(self, file):
        whitespace_locs = []
        doc_no_whitespace = ''
        loc = 0
        for char in self._methods:
            if char == ' ':
                whitespace_locs.append(loc)
            else:
                doc_no_whitespace += char
                loc += 1
        with open(file + '/report.json', 'r', encoding='utf-8') as f:
            report_json = json.loads(f.read())
            for section in report_json['sections']:
                for sentence in section['srList']:
                    sentence['sentence'] = self._fix_sent(sentence['sentence'], doc_no_whitespace, whitespace_locs)
            for section in report_json['rigor-table']['sections']:
                for sentence in section['srList']:
                    if sentence['sentence'] != 'not detected.':
                        sentence['sentence'] = self._fix_sent(sentence['sentence'], doc_no_whitespace, whitespace_locs)
        with open(file + '/report.json', 'w', encoding='utf-8') as f:
            f.write(json.dumps(report_json))
        return

    def _fix_sent(self, sentence, doc_no_whitespace, whitespace_locs):
        sentence_no_whitespace = sentence.replace(' ', '')
        sent_loc = doc_no_whitespace.find(sentence_no_whitespace)
        fixed_sent = ''
        for j, i in enumerate(range(sent_loc, sent_loc + len(sentence_no_whitespace))):
            if i in whitespace_locs:
                fixed_sent += ' '
            fixed_sent += sentence_no_whitespace[j]
        return fixed_sent.strip()