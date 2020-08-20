import biorxiv
import pdftools
import os
import time
import random


time.sleep(5)
while True:
    time.sleep(random.random())
    ids = os.listdir('../papers')
    for id in ids:
        if os.path.exists('../papers/' + id) and not os.path.exists('../papers/' + id + '/extract_started'):
            open('../papers/' + id + '/extract_started', 'w').close()
            print('Started processing', id)
            doi = '10.1101/' + id
            paper = biorxiv.Paper(doi)
            folder = '../papers/' + doi.split('/')[1]
            pdf_path = folder + '/raw.pdf'
            paper.save_pdf(pdf_path)
            pdf = pdftools.PDF(pdf_path)
            methods = pdf.get_text('methods')
            discussion = pdf.get_text('discussion')
            all = pdf.get_text('all')
            with open(folder + '/methods.txt', 'w', encoding='utf-8') as f:
                f.write(methods)
            with open(folder + '/discussion.txt', 'w', encoding='utf-8') as f:
                f.write(discussion)
            with open(folder + '/all.txt', 'w', encoding='utf-8') as f:
                f.write(all)