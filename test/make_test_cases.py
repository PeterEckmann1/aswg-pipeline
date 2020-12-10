import os
import shutil
import json


def save_extractor_case(doi, is_biorxiv):
    r = extract(doi, is_biorxiv, False, False)
    r['date'] = r['date'].strftime('%Y-%m-%d')
    r['image_dir'] = os.listdir(r['image_dir'])
    open('test/extract_test_cases/{}.json'.format(doi.replace('/', '_')), 'w', encoding='utf-8').write(json.dumps(r))


def make_extractor_cases():
    save_extractor_case('10.1101/2020.11.25.20238915', False)
    save_extractor_case('10.1101/2020.11.10.374587', True)
    save_extractor_case('10.1101/2020.11.24.20238287', False)


def make_jetfighter_cases():
    from jetfighter import jetfighter
    extract('10.1101/2020.12.05.413377', True, False, False)
    extract('10.1101/2020.11.24.393629', True, False, False)
    extract('10.1101/2020.11.29.20240374', False, False, False)
    print(jetfighter(False, 3))


def save_text_section(doi, is_biorxiv, section, append=''):
    open('temp/{}/{}.txt'.format(section, doi.replace('/', '_')), 'w', encoding='utf-8').write(extract(doi, is_biorxiv, False, False)[section] + append)


def make_limitation_recognizer_cases():
    from limitation_recognizer import limitation_recognizer
    save_text_section('10.1101/2020.11.24.20238261', False, 'discussion')
    save_text_section('10.1101/2020.11.25.20235366', False, 'discussion')
    limitation_results = limitation_recognizer()
    for doi in limitation_results:
        print(doi, len(limitation_results[doi]['sents']))


def make_trial_identifier_cases():
    from trial_identifier import trial_identifier
    save_text_section('10.1101/2020.11.25.20235150', False, 'all_text')
    save_text_section('10.1101/2020.10.15.20209817', False, 'all_text')
    save_text_section('10.1101/2020.11.27.20239087', False, 'all_text')
    open('test/trial_identifier_test_cases.json', 'w', encoding='utf-8').write(json.dumps(trial_identifier(['10.1101/2020.11.25.20235150', '10.1101/2020.10.15.20209817', '10.1101/2020.11.27.20239087'])))


def make_sciscore_html_cases():
    from sciscore import sciscore
    save_text_section('10.1101/2020.11.25.20235150', False, 'methods')
    save_text_section('10.1101/2020.11.25.20238741', False, 'methods')
    save_text_section('10.1101/2020.11.10.374587', True, 'methods')
    save_text_section('10.1101/2020.12.04.20244137', False, 'methods')
    save_text_section('10.1101/2020.12.04.20244079', False, 'methods')
    result = sciscore()
    open('test/sciscore_html_test_cases.json', 'w', encoding='utf-8').write(json.dumps(result))

def make_barzooka_cases():
    from barzooka import barzooka
    extract('10.1101/2020.11.29.20240416', False, False, False)
    print(barzooka())

def make_oddpub_cases():
    from oddpub import oddpub
    save_text_section('10.1101/2020.11.29.20240481', False, 'all_text')
    save_text_section('10.1101/2020.11.25.20235150', False, 'all_text')
    save_text_section('10.1101/2020.11.25.20238899', False, 'all_text')
    save_text_section('10.1101/2020.11.28.20240325', False, 'all_text')
    print(oddpub())


if __name__ == '__main__':
    os.chdir('../')
    shutil.rmtree('temp')
    os.mkdir('temp')
    os.mkdir('temp/discussion')
    os.mkdir('temp/methods')
    os.mkdir('temp/all_text')
    os.mkdir('temp/images')
    from extractor import extract
    make_oddpub_cases()