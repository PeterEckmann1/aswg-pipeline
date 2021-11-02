from utils.extractor import biorxiv
from utils.extractor import pdftools


def get_section_from_text(text, section_name):
    section_text = ''
    if section_name == 'discussion':
        for section in text:
            if 'discussion' in section['header'].lower():
                section_text += section['content'] + ' '
    if section_name == 'methods':
        for section in text:
            if 'method' in section['header'].lower() or 'study design' in section['header'].lower() or 'procedure' in section['header'].lower() or 'materials' in section['header'].lower():
                section_text += section['content'] + ' '
    if section_name == 'all':
        for section in text:
            section_text += section['content'] + ' '
    return section_text.replace('\n','').replace('  ', ' ').strip()


def extract(doi, is_biorxiv, force_pdf, use_scaled):
    preprint = biorxiv.Preprint(doi, is_biorxiv)
    pdf_name = 'temp/' + doi.replace('/', '_') + '.pdf'
    preprint.get_pdf(pdf_name)
    metadata = preprint.get_metadata()
    pdf = pdftools.PDF(pdf_name, doi.replace('/', '_'))
    if preprint.is_full_text_html() and not force_pdf:
        text = preprint.get_full_text_html()
        return {'doi': doi, 'title': metadata['title'], 'abstract': metadata['abstract'], 'authors': metadata['authors'], 'date': metadata['date'], 'full_text_html': True, 'url': preprint.url, 'discussion': get_section_from_text(text, 'discussion'), 'methods': get_section_from_text(text, 'methods'), 'all_text': get_section_from_text(text, 'all') + ' ' + preprint.get_data_code_statement() + ' ' + metadata['abstract'], 'image_dir': pdf.get_images(use_scaled)}
    else:
        return {'doi': doi, 'title': metadata['title'], 'abstract': metadata['abstract'], 'authors': metadata['authors'], 'date': metadata['date'], 'full_text_html': False, 'url': preprint.url, 'discussion': pdf.get_text('discussion'), 'methods': pdf.get_text('methods'), 'all_text': pdf.get_text('all') + ' ' + preprint.get_data_code_statement() + ' ' + metadata['abstract'], 'image_dir': pdf.get_images(use_scaled)}


def extract_worker(args):
    safe_doi = args['doi'].replace('/', '_')
    preprint = extract(args['doi'], args['doi_source'], args['force_pdf'], args['use_scaled'])
    metadata = {'url': preprint['url'],
                'title': preprint['title'],
                'abstract': preprint['abstract'],
                'authors': preprint['authors'],
                'date': preprint['date']}
    is_full_text_html = preprint['full_text_html']
    discussion = preprint['discussion']
    methods = preprint['methods']
    all_text = preprint['all_text']
    open('temp/discussion/' + safe_doi + '.txt', 'w', encoding='utf-8').write(discussion)
    open('temp/methods/' + safe_doi + '.txt', 'w', encoding='utf-8').write(methods)
    open('temp/all_text/' + safe_doi + '.txt', 'w', encoding='utf-8').write(all_text)
    return args['doi'], metadata, is_full_text_html, (discussion, methods, all_text)
