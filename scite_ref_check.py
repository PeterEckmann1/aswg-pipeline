import os
import requests
from tqdm import tqdm
import time


def get_message(num_retracted, num_errata):
    message = ''
    if num_retracted == 1:
        message = 'one unreliable citation'
    elif num_retracted > 1:
        message = 'unreliable citations'
    if num_retracted > 0 and num_errata > 0:
        message += ' and '
    if num_errata == 1:
        message += 'one citation with an erratum'
    elif num_errata > 1:
        message += 'citations with errata'
    message += '. '
    if num_retracted > 0:
        message += 'If you need to cite a retracted paper, we recommend noting at the beginning of the citation that the paper is retracted (i.e. RETRACTED: Title of paper, authors, journal, etc.). '
    if num_errata > 0:
        if num_retracted > 0:
            if num_errata == 1:
                message += 'We also recommend checking the erratum to confirm that it does not impact the accuracy of your citation. '
            else:
                message += 'We also recommend checking the errata to confirm that they do not impact the accuracy of your citation. '
        else:
            if num_errata == 1:
                message += 'We recommend checking the erratum to confirm that it does not impact the accuracy of your citation. '
            else:
                message += 'We recommend checking the errata to confirm that they do not impact the accuracy of your citation. '
    return message.strip()


def scite_ref_check(dois):
    output = {}
    scite_ids = []
    for f_name in tqdm([f_name for f_name in os.listdir('temp') if '.pdf' in f_name], desc='submitting to reference check'):
        scite_ids.append(requests.post('https://api.scite.ai/reference_check',
                                       headers={'Authorization': 'Bearer ' + os.environ['SCITE_TOKEN']},
                                       files={'pdf': open('temp/' + f_name, 'rb')}).json()['id'])
    for i, f_name in enumerate(tqdm([f_name for f_name in os.listdir('temp') if '.pdf' in f_name], desc='waiting for reference check')):
        response = requests.get('https://api.scite.ai/reference_check/tasks/' + scite_ids[i]).json()
        while response['status'] == 'STARTED':
            response = requests.get('https://api.scite.ai/reference_check/tasks/' + scite_ids[i]).json()
            time.sleep(1)
        output[dois[i]] = {'raw_json': response}
        papers = [response['papers'][doi] for doi in response['papers'] if response['papers'][doi]['retracted']]
        if len(papers) == 0:
            output[dois[i]]['html'] = '<p><i>Results from <a href="https://medium.com/scite/reference-check-an-easy-way-to-check-the-reliability-of-your-references-b2afcd64abc6">scite Reference Check</a></i>: We found no unreliable references.</p>'
            continue
        row_html = []
        num_retracted = 0
        num_errata = 0
        for paper in papers:
            row = '<tr>' \
                  f'<td style="min-width:95px; border: 1px solid lightgray; padding:2px"><a href="{"https://www.doi.org/" + paper["doi"]}">{paper["doi"]}</a></td>' \
                  f'<td style="min-width:95px; border: 1px solid lightgray; padding:2px">{paper["retracted"]}</td>' \
                  f'<td style="min-width:95px; border: 1px solid lightgray; padding:2px">{paper["title"][:60] + ("…" if len(paper["title"]) > 60 else "")}</td>' \
                  f'</tr>'
            if paper['retracted'] == 'Retracted':
                num_retracted += 1
                row_html.insert(0, row)
            elif paper['retracted'] == 'Has erratum' or paper['retracted'] == 'Has correction':
                num_errata += 1
                row_html.append(row)
            else:
                raise Exception('Unexpected reference type', paper['retracted'])
        output[dois[i]]['html'] = '<p><i>Results from <a href="https://medium.com/scite/reference-check-an-easy-way-to-check-the-reliability-of-your-references-b2afcd64abc6">scite Reference Check</a></i>: We found ' + get_message(num_retracted, num_errata) + '</p><table style="border-collapse: collapse;"><tr><th style="min-width:95px; border: 1px solid lightgray; padding:2px">DOI</th><th style="min-width:95px; border: 1px solid lightgray; padding:2px">Status</th><th style="min-width:95px; border: 1px solid lightgray; padding:2px">Title</th></tr>' + ''.join(row_html) + '</table>'
    return output


#import json
#open('test.json', 'w', encoding='utf-8').write(json.dumps(scite_ref_check(['1', '2', '3', '4'])))