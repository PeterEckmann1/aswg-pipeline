import os
import requests
from tqdm import tqdm
import time
import sys


def fetch_from_api(scite_ids, dois):
    output = {}
    for i, scite_id in enumerate(scite_ids):
        if not scite_id:
            print('ref check conn refused', file=sys.stderr)
            output[dois[i]] = {'raw_json': None}
            continue
        response = requests.get('https://api.scite.ai/reference_check/tasks/' + scite_id).json()
        while response['status'] == 'STARTED' or response['status'] == 'PENDING':
            response = requests.get('https://api.scite.ai/reference_check/tasks/' + scite_id).json()
            print(f"response: {response['status']}", file=sys.stderr)
            time.sleep(5)
        output[dois[i]] = {'raw_json': response}
    return output


def scite_ref_check(dois):
    output = {}
    current_dois = []
    scite_ids = []
    for i, f_name in enumerate(tqdm([f_name for f_name in os.listdir('temp') if '.pdf' in f_name], desc='reference check')):
        current_dois.append(dois[i])
        try:
            print('submitting request', file=sys.stderr)
            # res = requests.post('https://api.scite.ai/reference_check',
            #                     headers={'Authorization': 'Bearer ' + os.environ['SCITE_TOKEN']},
            #                     files={'pdf': open('temp/' + f_name, 'rb')}, timeout=5)
            # if res.status_code != 200:
            return {dois[0]: {'raw_json': {'status': 'FAILURE'}}}
            res = res.json()
            if res['message'] == 'An unexpected error occurred':
                return {dois[0]: {'raw_json': {'status': 'FAILURE'}}}
            scite_ids.append(res['id'])
        except requests.exceptions.ConnectionError:
            scite_ids.append(None)
        if len(scite_ids) > 10:
            output = {**output, **fetch_from_api(scite_ids, current_dois)}
            scite_ids = []
            current_dois = []
    print('fetching results', file=sys.stderr)
    output = {**output, **fetch_from_api(scite_ids, current_dois)}
    return output
