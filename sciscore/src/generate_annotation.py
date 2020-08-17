import os
import json
from paper_type_classifier import predict_if_model_paper
import sciscore
from collections import defaultdict
import re
import shutil
import time
import random


def generate_html(json_obj, discard_rigor):
    html = f"""<p>SciScore for <i>{json_obj['docIdentifier']}</i>:  (<a href="https://www.sciscore.com/index.html#faqs">What is this?)</a></p><p>Please note, not all rigor criteria are appropriate for all manuscripts.</p>"""

    if discard_rigor:
        rigor_table = '<i>NIH rigor criteria are not applicable to paper type.</i>'
    else:
        rigor_table = '<table>'
        for section in json_obj['rigor-table']['sections']:
            title = section['title']
            text = section['srList'][0]['sentence']
            rigor_table += f'<tr"><td style="min-width:100px;margin-right:1em; border-right:1px solid lightgray; border-bottom:1px solid lightgray">{title}</td><td style="min-width:100px;border-bottom:1px solid lightgray">{text}</td></tr>'
        rigor_table += '</table>'

    if len(json_obj['sections']) == 0:
        resource_table = '<p><i>No key resources detected.</i></p>'
    else:
        resource_table = '<table>'
        for section in json_obj['sections']:
            title = section['sectionName']
            resource_table += f'<tr><td style="min-width:100px;text-align:center; padding-top:4px;" colspan="2"><b>{title}</b></td></tr>'
            resource_table += '<tr><td style="min-width:100px;text=align:center"><i>Sentences</i></td><td style="min-width:100px;text-align:center"><i>Resources</i></td></tr>'
            sentences = []
            mentions = defaultdict(list)
            for item in section['srList']:
                sentence = item['sentence']
                sentences.append(sentence)
                for mention in item['mentions']:
                    identifier = mention['rrid']
                    detected = True
                    if identifier is None:
                        if 'suggestedRrid' in mention.keys():
                            identifier = mention['suggestedRrid']
                        detected = False
                    identifier = str(identifier)
                    identifier = identifier.replace(')', '')
                    if 'RRID:' in identifier:
                        rrid = identifier.split('RRID:')[1].strip().replace(')', '')
                        identifier = identifier.replace('RRID:', 'RRID:<a href="https://scicrunch.org/resources/Any/search?q=') + '">' + rrid + '</a>)'
                    mentions[sentence].append({'source': mention['source'], 'term': mention['neText'], 'identifier': identifier, 'detected': detected})
            for sentence in sentences:
                mention_texts = []
                for mention in mentions[sentence]:
                    if mention['detected']:
                        mention_texts.append(f"""
                                              <div style="margin-bottom:8px">
                                                <div><b>{mention['term']}</b></div>
                                                <div>detected: {mention['identifier']}</div>
                                              </div>
                                            """)
                    else:
                        mention_texts.append(f"""
                                              <div style="margin-bottom:8px">
                                                <div><b>{mention['term']}</b></div>
                                                <div>suggested: {mention['identifier']}</div>
                                              </div>
                                            """)
                mention_text = ''.join(mention_texts)
                resource_table += f'<tr><td style="min-width:100px;vertical-align:top;border-bottom:1px solid lightgray">{sentence}</td><td style="min-width:100px;border-bottom:1px solid lightgray">{mention_text}</td></tr>'
        resource_table += '</table>\n'

    html += f'<p><b>Table 1: Rigor</b></p>{rigor_table}<p><b>Table 2: Resources</b></p>{resource_table}'

    html += """
      <p><b>About SciScore</b></p>
      <p>SciScore is an automated tool that is designed to assist expert reviewers by finding and presenting formulaic 
      information scattered throughout a paper in a standard, easy to digest format. SciScore checks for the presence 
      and correctness of RRIDs (research resource identifiers), and for rigor criteria such as sex and 
      investigator blinding. For details on the theoretical underpinning of rigor criteria and the tools shown here, 
      including references cited, please follow <a href="https://docs.google.com/document/d/1fY0Uze8b4udlPGDLNfAXgFiXzxUeACLssA_lieKMqTI/edit">this link</a>.
      """

    return html


time.sleep(20)
while True:
    time.sleep(random.random())
    ids = os.listdir('../papers')
    for id in ids:
        if not os.path.exists('../papers/' + id + '/sciscore.html') and os.path.exists('../papers/' + id + '/methods.txt') and not os.path.exists('../papers/' + id + '/sciscore_started'):
            open('../papers/' + id + '/sciscore_started', 'w').close()
            print('Started processing', id)
            with open('../papers/' + id + '/methods.txt', 'r', encoding='utf-8') as f:
                methods = f.read()
            if methods == '':
                print('Blank methods, blank report being used')
                with open('../papers/' + id + '/sciscore_db.txt', 'w', encoding='utf-8') as f:
                    f.write('SciScore error, blank report')
                with open('../papers/' + id + '/sciscore.html', 'w', encoding='utf-8') as f:
                    print('Error in SciScore, blank report being used.')
                    f.write(generate_html({'sections': [], 'docIdentifier': '10.1101/' + id}, True))
                continue
            paper = sciscore.Paper(methods, '10.1101/' + id)
            paper.download_report('temp.zip')
            with open('temp.zip/report.json', 'r', encoding='utf-8') as f:
                file_contents = f.read()
            raw = json.loads(file_contents)
            raw['docIdentifier'] = raw['docIdentifier'].replace('_', '/')
            html = generate_html(raw, predict_if_model_paper(methods))
            shutil.rmtree('temp.zip')
            with open('../papers/' + id + '/sciscore_db.txt', 'w', encoding='utf-8') as f:
                f.write(file_contents)
            with open('../papers/' + id + '/sciscore.html', 'w', encoding='utf-8') as f:
                f.write(html)