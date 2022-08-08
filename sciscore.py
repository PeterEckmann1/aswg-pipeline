import json
from utils.sciscore.paper_type_classifier import predict_if_model_paper
from utils.sciscore.sciscore_api import SciScore
from collections import defaultdict
import os
from tqdm import tqdm
import time


def sciscore():
    output = {}
    for f_name in tqdm(os.listdir('temp/methods'), desc='sciscore'):
        doi = f_name.replace('_', '/').replace('.txt', '')
        methods = open('temp/methods/' + f_name, 'r', encoding='utf-8').read()
        paper = SciScore(methods, doi)
        zip_name = 'temp/' + f_name.replace('.txt', '.zip')
        paper.get_report(zip_name)
        raw = json.loads(open(zip_name + '/report.json', 'r', encoding='utf-8').read())
        raw['docIdentifier'] = raw['docIdentifier'].replace('_', '/')
        is_modeling = bool(predict_if_model_paper(methods))
        output[doi] = {'raw_json': raw, 'is_modeling_paper': is_modeling}
        time.sleep(5)
    return output
