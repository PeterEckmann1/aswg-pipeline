import json
from utils.sciscore.paper_type_classifier import predict_if_model_paper
from utils.sciscore.sciscore_api import SciScore
from collections import defaultdict
import os
from tqdm import tqdm
import time


def generate_html(json_obj, discard_rigor):
    html = f"""<p>SciScore for <i>{json_obj['docIdentifier']}</i>:  (<a href="https://www.sciscore.com/index.html#faqs">What is this?</a>)</p><p>Please note, not all rigor criteria are appropriate for all manuscripts.</p>"""
    if discard_rigor:
        rigor_table = '<i>NIH rigor criteria are not applicable to paper type.</i>'
    else:
        rigor_table = '<table>'
        for section in json_obj['rigor-table']['sections']:
            title = section['title']
            text_sections = []
            for i, sr in enumerate(section['srList']):
                if 'title' in sr:
                    text_sections.append(f"{sr['title']}: {sr['sentence']}")
                else:
                    text_sections.append(sr['sentence'])
            text = '<br>'.join(text_sections)
            rigor_table += f'<tr><td style="min-width:100px;margin-right:1em; border-right:1px solid lightgray; border-bottom:1px solid lightgray">{title}</td><td style="min-width:100px;border-bottom:1px solid lightgray">{text}</td></tr>'
        rigor_table += '</table>'
    if len(json_obj['sections']) == 0:
        resource_table = '<p><i>No key resources detected.</i></p>'
    else:
        resource_table = '<table>'
        for section in json_obj['sections']:
            title = section['sectionName']
            resource_table += f'<tr><th style="min-width:100px;text-align:center; padding-top:4px;" colspan="2">{title}</th></tr>'
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
                        mention_texts.append(f'<div style="margin-bottom:8px"><div><b>{mention["term"]}</b></div><div>detected: {mention["identifier"]}</div></div>')
                    else:
                        mention_texts.append(f'<div style="margin-bottom:8px"><div><b>{mention["term"]}</b></div><div>suggested: {mention["identifier"]}</div></div>')
                mention_text = ''.join(mention_texts)
                resource_table += f'<tr><td style="min-width:100px;vertical-align:top;border-bottom:1px solid lightgray">{sentence}</td><td style="min-width:100px;border-bottom:1px solid lightgray">{mention_text}</td></tr>'
        resource_table += '</table>'
    html += f'<p><b>Table 1: Rigor</b></p>{rigor_table}<p><b>Table 2: Resources</b></p>{resource_table}'
    html += '<hr>{}<hr><footer><p><b>About SciScore</b></p><p>SciScore is an automated tool that is designed to assist expert reviewers by finding and presenting formulaic information scattered throughout a paper in a standard, easy to digest format. SciScore checks for the presence and correctness of RRIDs (research resource identifiers), and for rigor criteria such as sex and investigator blinding. For details on the theoretical underpinning of rigor criteria and the tools shown here, including references cited, please follow <a href="https://scicrunch.org/ASWG/about/References">this link</a>.</p></footer>'
    return html


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
        html = generate_html(raw, is_modeling)
        output[doi] = {'html': html, 'raw_json': raw, 'is_modeling_paper': is_modeling}
        time.sleep(5)
    return output
