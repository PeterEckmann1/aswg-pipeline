from fastapi import FastAPI, UploadFile, File
from secrets import token_hex
from utils.extractor import pdftools
import os
from jetfighter import jetfighter
from limitation_recognizer import limitation_recognizer
from trial_identifier import trial_identifier
from barzooka import barzooka
from sciscore import sciscore
from oddpub import oddpub
from scite_ref_check import scite_ref_check
from rtransparent import rtransparent
from generate_html import generate_html
import shutil
from unidecode import unidecode


app = FastAPI()
token_to_filename = {}


@app.post('/upload')
async def upload(file: UploadFile = File(...)):
    token = token_hex(16)
    token_to_filename[token] = file.filename
    if os.path.exists('temp'):
        shutil.rmtree('temp')
    os.mkdir('temp')
    os.mkdir('temp/discussion')
    os.mkdir('temp/methods')
    os.mkdir('temp/all_text')
    os.mkdir('temp/images')
    f_name = f'temp/{token}.pdf'
    contents = await file.read()
    open(f_name, 'wb').write(contents)
    pdf = pdftools.PDF(f_name, token)
    pdf.get_images(False)
    return {'token': token, 'methods': unidecode(pdf.get_text('methods')), 'discussion': unidecode(pdf.get_text('discussion')), 'all': unidecode(pdf.get_text('all'))}


@app.post('/report')
async def report(token, methods, discussion, all):
    open(f'temp/discussion/{token}.txt', 'w', encoding='utf-8').write(discussion)
    open(f'temp/methods/{token}.txt', 'w', encoding='utf-8').write(methods)
    open(f'temp/all_text/{token}.txt', 'w', encoding='utf-8').write(all)
    import sys
    print('running jetfighter', file=sys.stderr)
    jetfighter_results = jetfighter(False, 1)
    print('running limitation', file=sys.stderr)
    limitation_recognizer_results = limitation_recognizer()
    print('running trial id', file=sys.stderr)
    trial_identifier_results = trial_identifier([token])
    print('running sciscore', file=sys.stderr)
    sciscore_results = sciscore()
    print('running barzooka', file=sys.stderr)
    barzooka_results = barzooka()
    print('running oddpub', file=sys.stderr)
    oddpub_results = oddpub()
    print('running ref check', file=sys.stderr)
    reference_check_results = scite_ref_check([token])
    print('running rtransparent', file=sys.stderr)
    rtransparent_results = rtransparent()
    return {'html': generate_html(token, token_to_filename[token], jetfighter_results, limitation_recognizer_results, trial_identifier_results, sciscore_results, barzooka_results, oddpub_results, reference_check_results, rtransparent_results)}