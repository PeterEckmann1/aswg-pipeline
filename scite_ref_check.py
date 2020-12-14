import os
import requests
from tqdm import tqdm


def scite_ref_check(dois):
    output = {}
    for i, f_name in enumerate(tqdm([f_name for f_name in os.listdir('temp') if '.pdf' in f_name], desc='reference check')):
        scite_id = '1d76aeb5-dbc4-443d-963b-73548580772e'#requests.post('https://api.scite.ai/reference_check',
                                    #headers={'Authorization': 'Bearer ' + os.environ['SCITE_TOKEN']},
                                    #files={'pdf': open('temp/' + f_name, 'rb')}).json()['id']
        response = requests.get('https://api.scite.ai/reference_check/tasks/' + scite_id).json()
        output[dois[i]] = {'raw_json': response}
        papers = [response['papers'][doi] for doi in response['papers'] if response['papers'][doi]['retracted']]
        if len(papers) == 0:
            output[dois[i]]['html'] = '<p><i>Results from <a href="https://medium.com/scite/reference-check-an-easy-way-to-check-the-reliability-of-your-references-b2afcd64abc6">scite Reference Check</a></i>: We found no unreliable references.</p>'
            continue
        table_html = '<table><td style="min-width:95px; border-right:1px solid lightgray; border-bottom:1px solid lightgray">DOI</td><td style="min-width:95px; border-right:1px solid lightgray; border-bottom:1px solid lightgray">Status</td><td style="min-width:95px; border-right:1px solid lightgray; border-bottom:1px solid lightgray">Title</td></tr>'
        for paper in papers:
            table_html += '<tr>' \
                          f'<td style="min-width:95px; border-right:1px solid lightgray; border-bottom:1px solid lightgray">{paper["doi"]}</td>' \
                          f'<td style="min-width:95px; border-right:1px solid lightgray; border-bottom:1px solid lightgray">{paper["retracted"]}</td>'\
                          f'<td style="min-width:95px; border-right:1px solid lightgray; border-bottom:1px solid lightgray">{paper["title"][:60] + ("…" if len(paper["title"]) > 60 else "")}</td>' \
                          '</tr>'
        output[dois[i]]['html'] = '<p><i>Results from <a href="https://medium.com/scite/reference-check-an-easy-way-to-check-the-reliability-of-your-references-b2afcd64abc6">scite Reference Check</a></i>: We found the following unreliable references:<br>' + table_html + '</table></p>'
    return output
