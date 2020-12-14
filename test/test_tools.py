import unittest
import os
import shutil
import json


os.chdir('../')


#todo CLINICAL TRIALS NOT WORKING, mock requests, check unresolved clinical trial numbers and multiple in a table
class TestExtractor(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        if os.path.exists('temp'):
            shutil.rmtree('temp')
        os.mkdir('temp')
        os.mkdir('temp/discussion')
        os.mkdir('temp/methods')
        os.mkdir('temp/all_text')
        os.mkdir('temp/images')

        from extractor import extract
        self.responses = {'10.1101/2020.11.25.20238915': self.normalize_json(extract('10.1101/2020.11.25.20238915', False, False, False)),
                          '10.1101/2020.11.10.374587': self.normalize_json(extract('10.1101/2020.11.10.374587', True, False, False)),
                          '10.1101/2020.11.24.20238287': self.normalize_json(extract('10.1101/2020.11.24.20238287', False, False, False))}
        self.test_cases = {'10.1101/2020.11.25.20238915': json.loads(open('test/extract_test_cases/10.1101_2020.11.25.20238915.json', 'r', encoding='utf-8').read()),
                           '10.1101/2020.11.10.374587': json.loads(open('test/extract_test_cases/10.1101_2020.11.10.374587.json', 'r', encoding='utf-8').read()),
                           '10.1101/2020.11.24.20238287': json.loads(open('test/extract_test_cases/10.1101_2020.11.24.20238287.json', 'r', encoding='utf-8').read())}

    @classmethod
    def tearDownClass(self):
        shutil.rmtree('temp')

    @classmethod
    def normalize_json(self, r):
        r['date'] = r['date'].strftime('%Y-%m-%d')
        r['image_dir'] = os.listdir(r['image_dir'])
        return r

    def test_title(self):
        self.assertEqual(self.responses['10.1101/2020.11.25.20238915']['title'], self.test_cases['10.1101/2020.11.25.20238915']['title'])
        self.assertEqual(self.responses['10.1101/2020.11.10.374587']['title'], self.test_cases['10.1101/2020.11.10.374587']['title'])
        self.assertEqual(self.responses['10.1101/2020.11.24.20238287']['title'], self.test_cases['10.1101/2020.11.24.20238287']['title'])

    def test_abstract(self):
        self.assertEqual(self.responses['10.1101/2020.11.25.20238915']['abstract'], self.test_cases['10.1101/2020.11.25.20238915']['abstract'])
        self.assertEqual(self.responses['10.1101/2020.11.10.374587']['abstract'], self.test_cases['10.1101/2020.11.10.374587']['abstract'])
        self.assertEqual(self.responses['10.1101/2020.11.24.20238287']['abstract'], self.test_cases['10.1101/2020.11.24.20238287']['abstract'])

    def test_authors(self):
        self.assertListEqual(self.responses['10.1101/2020.11.25.20238915']['authors'], self.test_cases['10.1101/2020.11.25.20238915']['authors'])
        self.assertListEqual(self.responses['10.1101/2020.11.10.374587']['authors'], self.test_cases['10.1101/2020.11.10.374587']['authors'])
        self.assertListEqual(self.responses['10.1101/2020.11.24.20238287']['authors'], self.test_cases['10.1101/2020.11.24.20238287']['authors'])

    def test_date(self):
        self.assertEqual(self.responses['10.1101/2020.11.25.20238915']['date'], self.test_cases['10.1101/2020.11.25.20238915']['date'])
        self.assertEqual(self.responses['10.1101/2020.11.10.374587']['date'], self.test_cases['10.1101/2020.11.10.374587']['date'])
        self.assertEqual(self.responses['10.1101/2020.11.24.20238287']['date'], self.test_cases['10.1101/2020.11.24.20238287']['date'])

    def test_url(self):
        self.assertEqual(self.responses['10.1101/2020.11.25.20238915']['url'], self.test_cases['10.1101/2020.11.25.20238915']['url'])
        self.assertEqual(self.responses['10.1101/2020.11.10.374587']['url'], self.test_cases['10.1101/2020.11.10.374587']['url'])
        self.assertEqual(self.responses['10.1101/2020.11.24.20238287']['url'], self.test_cases['10.1101/2020.11.24.20238287']['url'])

    def test_discussion(self):
        self.assertEqual(self.responses['10.1101/2020.11.25.20238915']['discussion'], self.test_cases['10.1101/2020.11.25.20238915']['discussion'])
        self.assertEqual(self.responses['10.1101/2020.11.10.374587']['discussion'], self.test_cases['10.1101/2020.11.10.374587']['discussion'])
        self.assertEqual(self.responses['10.1101/2020.11.24.20238287']['discussion'], self.test_cases['10.1101/2020.11.24.20238287']['discussion'])

    def test_methods(self):
        self.assertEqual(self.responses['10.1101/2020.11.25.20238915']['methods'], self.test_cases['10.1101/2020.11.25.20238915']['methods'])
        self.assertEqual(self.responses['10.1101/2020.11.10.374587']['methods'], self.test_cases['10.1101/2020.11.10.374587']['methods'])
        self.assertEqual(self.responses['10.1101/2020.11.24.20238287']['methods'], self.test_cases['10.1101/2020.11.24.20238287']['methods'])

    def test_all_text(self):
        self.assertEqual(self.responses['10.1101/2020.11.25.20238915']['all_text'], self.test_cases['10.1101/2020.11.25.20238915']['all_text'])
        self.assertEqual(self.responses['10.1101/2020.11.10.374587']['all_text'], self.test_cases['10.1101/2020.11.10.374587']['all_text'])
        self.assertEqual(self.responses['10.1101/2020.11.24.20238287']['all_text'], self.test_cases['10.1101/2020.11.24.20238287']['all_text'])

    def test_images(self):
        self.assertListEqual(self.responses['10.1101/2020.11.25.20238915']['image_dir'], self.test_cases['10.1101/2020.11.25.20238915']['image_dir'])
        self.assertListEqual(self.responses['10.1101/2020.11.10.374587']['image_dir'], self.test_cases['10.1101/2020.11.10.374587']['image_dir'])
        self.assertListEqual(self.responses['10.1101/2020.11.24.20238287']['image_dir'], self.test_cases['10.1101/2020.11.24.20238287']['image_dir'])


class TestTools(unittest.TestCase):
    def setUp(self):
        if os.path.exists('temp'):
            shutil.rmtree('temp')
        os.mkdir('temp')

    @classmethod
    def tearDownClass(self):
        shutil.rmtree('temp')

    def test_jetfighter(self):
        from jetfighter import jetfighter
        shutil.copytree('test/jetfighter_test_images', 'temp/images')
        result = jetfighter(False, 3)
        self.assertListEqual(result['10.1101/2020.11.29.20240374']['page_nums'], [])
        self.assertListEqual(result['10.1101/2020.12.05.413377']['page_nums'], [25])
        self.assertListEqual(result['10.1101/2020.11.24.393629']['page_nums'], [21, 40, 41])

    def test_limitation_recognizer(self):
        from limitation_recognizer import limitation_recognizer
        shutil.copytree('test/limitation_recognizer_test_text', 'temp/discussion')
        result = limitation_recognizer()
        self.assertEqual(len(result['10.1101/2020.11.24.20238261']['sents']), 0)
        self.assertEqual(len(result['10.1101/2020.11.25.20235366']['sents']), 9)

    def test_trial_identifier(self):
        from trial_identifier import trial_identifier
        shutil.copytree('test/trial_identifier_test_text', 'temp/all_text')
        result = trial_identifier(['10.1101/2020.11.25.20235150', '10.1101/2020.10.15.20209817', '10.1101/2020.11.27.20239087'])
        correct_result = json.loads(open('test/trial_identifier_test_cases.json', 'r', encoding='utf-8').read())
        self.assertEqual(result['10.1101/2020.11.25.20235150']['html'],
                         correct_result['10.1101/2020.11.25.20235150']['html'])
        self.assertEqual(json.dumps(result['10.1101/2020.11.25.20235150']['html']),
                         json.dumps(correct_result['10.1101/2020.11.25.20235150']['html']))

        self.assertEqual(result['10.1101/2020.10.15.20209817']['html'],
                         correct_result['10.1101/2020.10.15.20209817']['html'])
        self.assertEqual(json.dumps(result['10.1101/2020.10.15.20209817']['html']),
                         json.dumps(correct_result['10.1101/2020.10.15.20209817']['html']))

        self.assertEqual(result['10.1101/2020.11.27.20239087']['html'],
                         correct_result['10.1101/2020.11.27.20239087']['html'])
        self.assertEqual(json.dumps(result['10.1101/2020.11.27.20239087']['html']),
                         json.dumps(correct_result['10.1101/2020.11.27.20239087']['html']))

    def test_sciscore_html(self):
        from sciscore import generate_html
        correct_result = json.loads(open('test/sciscore_html_test_cases.json', 'r', encoding='utf-8').read())
        self.assertEqual(generate_html(correct_result['10.1101/2020.11.10.374587']['raw_json'], False), correct_result['10.1101/2020.11.10.374587']['html'])
        self.assertEqual(generate_html(correct_result['10.1101/2020.11.25.20235150']['raw_json'], False), correct_result['10.1101/2020.11.25.20235150']['html'])
        self.assertEqual(generate_html(correct_result['10.1101/2020.11.25.20238741']['raw_json'], False), correct_result['10.1101/2020.11.25.20238741']['html'])
        self.assertEqual(generate_html(correct_result['10.1101/2020.12.04.20244079']['raw_json'], False), correct_result['10.1101/2020.12.04.20244079']['html'])
        self.assertEqual(generate_html(correct_result['10.1101/2020.12.04.20244137']['raw_json'], True), correct_result['10.1101/2020.12.04.20244137']['html'])

    def test_barzooka(self):
        from barzooka import barzooka
        shutil.copytree('test/barzooka_test_images', 'temp/images')
        result = barzooka()
        self.assertDictEqual(result['10.1101/2020.11.29.20240416']['graph_types'], {'bar': 1, 'pie': 0, 'hist': 7, 'bardot': 1, 'box': 0, 'dot': 0, 'violin': 0})

    def test_oddpub(self):
        from oddpub import oddpub
        shutil.copytree('test/oddpub_test_text', 'temp/all_text')
        result = oddpub()
        self.assertFalse(result['10.1101/2020.11.25.20235150']['open_code'])
        self.assertTrue(result['10.1101/2020.11.25.20235150']['open_data'])

        self.assertTrue(result['10.1101/2020.11.25.20238899']['open_code'])
        self.assertFalse(result['10.1101/2020.11.25.20238899']['open_data'])

        self.assertFalse(result['10.1101/2020.11.28.20240325']['open_code'])
        self.assertFalse(result['10.1101/2020.11.28.20240325']['open_data'])

        self.assertTrue(result['10.1101/2020.11.29.20240481']['open_code'])
        self.assertTrue(result['10.1101/2020.11.29.20240481']['open_data'])


if __name__ == '__main__':
    unittest.main()