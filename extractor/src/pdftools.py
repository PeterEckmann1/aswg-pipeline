import subprocess
import os
from string import ascii_letters, ascii_uppercase
from collections import Counter
import fasttext
from spacy.lang.en import English
import re
import numpy as np
import hashlib


model = fasttext.load_model('methods-model.bin')
nlp = English()
sentencizer = nlp.create_pipe('sentencizer')
nlp.add_pipe(sentencizer)

REFERENCES_TERMS = ['Citations', 'CITATIONS', 'References', 'REFERENCES', 'Reference', 'REFERENCE', 'Bibliography', 'BIBLIOGRAPHY', 'Works Cited', 'WORKS CITED']
DISCUSSION_TERMS = ['Discussion', 'DISCUSSION', 'Discussion and Conclusion', 'Discussion and Conclusions', 'DISCUSSION AND CONCLUSION', 'DISCUSSION AND CONCLUSIONS']  #more terms could be added here, like results and discussion maybe? discussion ends terms were added, look at those and make sure they're good?
DISCUSSION_END_TERMS = ['Citations', 'CITATIONS', 'References', 'REFERENCES', 'Bibliography', 'BIBLIOGRAPHY', 'Works Cited', 'WORKS CITED', 'Acknowledgements', 'ACKNOWLEDGEMENTS', 'Acknowledgments', 'ACKNOWLEDGMENTS', 'Author contribution', 'Author contributions', 'AUTHOR CONTRIBUTION', 'AUTHOR CONTRIBUTIONS', 'Contributions', 'CONTRIBUTIONS', 'Conflicts of interest', 'CONFLICTS OF INTEREST', 'Conflict of interest', 'CONFLICT OF INTEREST', 'Data availability', 'DATA AVAILABILITY', 'Code availability', 'CODE AVAILABILITY', 'Figure legends', 'FIGURE LEGENDS', 'Figures', 'FIGURES', 'Conclusion', 'CONCLUSION', 'Conclusions', 'CONCLUSIONS']


class PDF:
    def __init__(self, file):
        self.file = file
        subprocess.call(['pdftotext', '-f', '2', file, file + '.txt'])
        try:
            with open(file + '.txt', 'r', encoding='utf-8') as f:
                self._text = f.read()
            os.remove(file + '.txt')
            self._text = self._remove_boilerplate(self._text)
        except FileNotFoundError:
            print('PDF could not be extracted, blank text being used')
            self._text = ''

    def _remove_boilerplate(self, text):
        text = text.replace('\n', ' <LINE_BREAK> ')
        pages = [f' {page} ' for page in text.split('')]
        num_regex = re.compile(' [0-9]+ ')
        hash_to_num = {}
        hashes = []
        for page in pages:
            for num_str in num_regex.findall(page):
                hash = hashlib.md5(num_str.encode('utf-8')).hexdigest()
                hashes.append(hash)
                hash_to_num[hash] = num_str
        pages = [self._remove_whitespace(num_regex.sub(' <NUMBER_PLACEHOLDER____________> ', f'<PAGE_START> {page} <PAGE_END>')) for page in pages]
        text = ' '.join(pages)
        remove_list = []
        for n in range(2, 100):
            unique_count = Counter()
            total_count = Counter()
            for page in pages:
                grams = self._n_grams(page.split(), n)
                for gram in grams:
                    total_count[gram] += 1
                for gram in set(grams):
                    unique_count[gram] += 1
            for match, unique in unique_count.most_common():
                if n < 10 and unique > len(pages) / 5:
                    if '<PAGE_START>' in match or '<PAGE_END>' in match:
                        remove_list.append(match)
                    elif '<LINE_BREAK>' in match and total_count[match] > len(pages) * 15:
                        remove_list.append(match)
                elif unique > len(pages) / 3:
                    remove_list.append(f' {match} ')
        remove_chars = np.zeros((len(text)))
        for phrase in remove_list:
            for match in re.finditer(re.escape(phrase), text):
                remove_chars[match.start(): match.end()] += 1
        for match in re.finditer('<LINE_BREAK>', text):
            remove_chars[match.start(): match.end()] = 0
        i = 0
        while '<NUMBER_PLACEHOLDER____________>' in text:
            text = text.replace('<NUMBER_PLACEHOLDER____________>', hashes[i], 1)
            i += 1
        text = ''.join([char for i, char in enumerate(text) if remove_chars[i] == 0])
        for hash in hash_to_num:
            text = text.replace(hash, hash_to_num[hash])
        text = self._remove_whitespace(text.replace('<PAGE_START>', ' ').replace('<PAGE_END>', ' ')).replace('<LINE_BREAK>', '\n')
        return text.replace('', 'ti').replace('ﬁ', 'fi').replace('ﬀ', 'ff')

    def _n_grams(self, tokens, n):
        grams = []
        for i in range(len(tokens) - n + 1):
            grams.append(' '.join(tokens[i: i + n]))
        return grams

    def _without_section(self, text, terms, keep_after):
        final = ''
        removing = False
        for line in text.split('\n'):
            cleaned = ''.join([char for char in line.rstrip().lstrip() if char in ascii_letters + ' ']).strip()
            if cleaned in terms:
                removing = True
                continue
            if keep_after and removing and len(cleaned.split()) < 5 and len(cleaned) > 2 and cleaned[0] in ascii_uppercase:
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
