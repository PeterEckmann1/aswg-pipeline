import subprocess
import os
import numpy as np
from string import ascii_letters, ascii_uppercase
from collections import Counter
import fasttext
from spacy.lang.en import English


model = fasttext.load_model('methods-model.bin')
nlp = English()
sentencizer = nlp.create_pipe('sentencizer')
nlp.add_pipe(sentencizer)

REFERENCES_TERMS = ['Citations', 'CITATIONS', 'References', 'REFERENCES', 'Bibliography', 'BIBLIOGRAPHY', 'Works Cited', 'WORKS CITED']
DISCUSSION_TERMS = ['Discussion', 'DISCUSSION']  #more terms could be added here, like results and discussion maybe? discussion ends terms were added, look at those and make sure they're good?
DISCUSSION_END_TERMS = ['Citations', 'CITATIONS', 'References', 'REFERENCES', 'Bibliography', 'BIBLIOGRAPHY', 'Works Cited', 'WORKS CITED', 'Acknowledgements', 'ACKNOWLEDGEMENTS', 'Acknowledgments', 'ACKNOWLEDGMENTS', 'Author contribution', 'Author contributions', 'AUTHOR CONTRIBUTION', 'AUTHOR CONTRIBUTIONS', 'Contributions', 'CONTRIBUTIONS', 'Conflicts of interest', 'CONFLICTS OF INTEREST', 'Conflict of interest', 'CONFLICT OF INTEREST', 'Data availability', 'DATA AVAILABILITY', 'Code availability', 'CODE AVAILABILITY', 'Figure legends', 'FIGURE LEGENDS', 'Figures', 'FIGURES', 'Conclusion', 'CONCLUSION', 'Conclusions', 'CONCLUSIONS']


class PDF:
    def __init__(self, file):
        self.file = file
        subprocess.call(['pdftotext', '-bbox', file, file + '.html'])
        with open(file + '.html', 'r', encoding='utf-8') as f:
            self._pages = self._parse(f.read())
        os.remove(file + '.html')
        self._text = self._boilerplate_remove(self._get_body_text_with_vertical_bounds())

    def _parse(self, raw):
        pages = []
        for line in raw.split('\n'):
            if '<page width="' in line:
                width = float(line.split('width="')[1].split('"')[0])
                height = float(line.split('height="')[1].split('"')[0])
                pages.append({'width': width, 'height': height, 'word_bbox': []})
            if '<word xMin="' in line:
                x_min = float(line.split('xMin="')[1].split('"')[0])
                y_min = float(line.split('yMin="')[1].split('"')[0])
                x_max = float(line.split('xMax="')[1].split('"')[0])
                y_max = float(line.split('yMax="')[1].split('"')[0])
                pages[-1]['word_bbox'].append((x_min, y_min, x_max, y_max))
        return pages

    def _get_body_text_with_vertical_bounds(self):
        arr = np.zeros((int(self._pages[0]['height']), int(self._pages[0]['width'])))
        for page in self._pages:
            for bbox in page['word_bbox']:
                arr[int(bbox[1]): int(bbox[3]), int(bbox[0]): int(bbox[2])] += 1
        x_min, x_max = self._horizontal_bounds(arr)
        y_min, y_max = 0, self._vertical_bounds(arr)[1]
        subprocess.call(['pdftotext', '-x', str(x_min), '-y', str(y_min), '-W', str(x_max - x_min), '-H', str(y_max - y_min),
             '-nopgbrk', '-f', '2', self.file, self.file + '.html'])
        with open(self.file + '.html', 'r', encoding='utf-8') as f:
            text = f.read()
        os.remove(self.file + '.html')
        text = text.replace('', 'ti').replace('ﬁ', 'fi')
        return text

    def _without_section(self, text, terms, keep_after):
        final = ''
        removing = False
        for line in text.split('\n'):
            cleaned = ''.join([char for char in line.rstrip().lstrip() if char in ascii_letters + ' ']).strip()
            if cleaned in terms:
                removing = True
                continue
            if keep_after and removing and len(cleaned.split()) < 5 and len(cleaned) > 2 and cleaned[
                0] in ascii_uppercase:
                removing = False
            if not removing:
                final += line + '\n'
        return final

    def _start_at_section(self, text, terms):
        final = ''
        reading = False
        for line in text.split('\n'):
            cleaned = ''.join([char for char in line.rstrip().lstrip() if char in ascii_letters + ' ']).strip()
            if cleaned in terms:
                reading = True
            if reading:
                final += line + '\n'
        return final

    def _count_nums(self, tokens):
        count = 0
        for token in tokens:
            try:
                float(token.replace('%', ''))
                count += 1
            except:
                pass
        return count

    def _horizontal_bounds(self, arr):
        proj = np.sum(arr, axis=0)
        if len(self._pages) < 15:
            thresh = 500
        else:
            thresh = 1000
        proj[proj < thresh] = 0
        proj[proj >= thresh] = 1
        x_min = int(proj.shape[0] * (1 / 3))
        x_max = int(proj.shape[0] * (2 / 3))
        try:
            while proj[x_min] == 1:
                x_min -= 1
        except IndexError:
            x_min += 1
        try:
            while proj[x_max] == 1:
                x_max += 1
        except IndexError:
            x_max -= 1
        return x_min - 1, x_max + 15

    def _peaks(self, arr):
        count = 0
        for i in range(arr.shape[0] - 1):
            if arr[i] == 0 and arr[i + 1] == 1:
                count += 1
        return count

    def _vertical_bounds(self, arr):
        proj = np.sum(arr, axis=1)
        if len(self._pages) <= 10:
            thresh = 500
        else:
            thresh = 800
        proj[proj < thresh] = 0
        proj[proj >= thresh] = 1
        for i in range(proj.shape[0] - 6):
            if proj[i] == 1 and proj[i + 1] == 0 and 1 in proj[i + 1: i + 19]:
                proj[i + 1] = 1
        leap = 25
        while self._peaks(proj) > 5:
            for i in range(proj.shape[0] - leap + 1):
                if proj[i] == 1 and proj[i + 1] == 0 and 1 in proj[i + 1: i + leap]:
                    proj[i + 1] = 1
            leap += 10
        y_min = int(proj.shape[0] / 2)
        y_max = y_min
        try:
            while proj[y_min] == 1:
                y_min -= 1
        except IndexError:
            y_min += 1
        try:
            while proj[y_max] == 1:
                y_max += 1
        except IndexError:
            y_max -= 1
        return y_min - 1, y_max + 1

    def _boilerplate_remove(self, text):
        lines = [line for line in text.split('\n') if line.strip() != '']
        count = Counter(lines)
        thresh = 4
        for line in count.most_common():
            if line[1] > thresh and len(line[0].strip()) > 10:
                text = text.replace(line[0], '')
        return text

    def _remove_whitespace(self, text):
        return ' '.join(text.replace('\n', ' ').split())

    def get_text(self, section):
        text = self._text
        if section == 'discussion':
            text = self._start_at_section(text, DISCUSSION_TERMS)
            text = self._without_section(text, DISCUSSION_END_TERMS, False)
            return self._remove_whitespace(text)
        elif section == 'methods':
            text = self._without_section(text, REFERENCES_TERMS, False)
            text = self._remove_whitespace(text)
            sents = []
            vals = []
            doc = nlp(text)
            for sent in doc.sents:
                vals.append(model.predict(sent.text)[0][0] == '__label__methods')
                sents.append(sent.text)
            for i in range(len(vals) - 3):
                if vals[i] and (vals[i + 2] or vals[i + 3]):
                    vals[i + 1] = 1
                    vals[i + 2] = 1
            text = ' '.join([sents[i] for i in range(len(vals)) if vals[i]])
            return text
        elif section == 'all':
            return self._remove_whitespace(text)
        else:
            raise TypeError('Invalid section')