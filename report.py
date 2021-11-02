#trial-identifier might need to use text from the pdf to extract identifiers in references
#clean up how data/code availability is extracted (especially removing markdown, or are the links in markdown useful?), including expanding what is extracted
#should barzooka get full page images instead of extracted images?
#change tweet link order so annotation shows in box
#clean up temp file after get_report runs, not before (or maybe both)
def get_reports(dois, doi_source=None, force_pdf=False, use_scaled=False, workers=10):
    from extractor import extract_worker
    from jetfighter import jetfighter
    from limitation_recognizer import limitation_recognizer
    from trial_identifier import trial_identifier
    from barzooka import barzooka
    from sciscore import sciscore
    from oddpub import oddpub
    from release import generate_tweet_text
    import shutil
    import os
    from tqdm import tqdm
    from multiprocessing import Pool
    from scite_ref_check import scite_ref_check
    from rtransparent import rtransparent

    if os.path.exists('temp'):
        shutil.rmtree('temp')
    os.mkdir('temp')
    os.mkdir('temp/discussion')
    os.mkdir('temp/methods')
    os.mkdir('temp/all_text')
    os.mkdir('temp/images')
    if use_scaled:
        os.mkdir('temp/images_scaled')

    extract_args = []
    for i, doi in enumerate(dois):
        extract_args.append({'doi': doi, 'doi_source': (doi_source[i] if doi_source else None), 'force_pdf': force_pdf, 'use_scaled': use_scaled})
    with Pool(workers) as pool:
        extracted = list(tqdm(pool.imap_unordered(extract_worker, extract_args), total=len(dois), desc='extracting'))
    doi_to_is_full_text_html = {}
    doi_to_metadata = {}
    doi_to_text = {}
    for doi, metadata, is_full_text_html, text in extracted:
        doi_to_metadata[doi] = metadata
        doi_to_is_full_text_html[doi] = is_full_text_html
        doi_to_text[doi] = text

    print('jetfighter running..')
    jetfighter_results = jetfighter(use_scaled, workers)
    print('limitation-recognizer running..')
    limitation_recognizer_results = limitation_recognizer()
    print('trial-identifier running..')
    trial_identifier_results = trial_identifier(dois)
    print('sciscore running')
    sciscore_results = sciscore()
    print('barzooka running..')
    barzooka_results = barzooka()
    print('oddpub running..')
    oddpub_results = oddpub()
    print('scite running..')
    reference_check_results = scite_ref_check(dois)
    print('rtransparent running..')
    rtransparent_results = rtransparent()

    output = {}
    for doi in dois:
        print('Generating output for doi ' + doi)
        html = sciscore_results[doi]['html'].replace('{}', 'FORMAT_PLACEHOLDER').replace('{', '(').replace('}', ')').replace('FORMAT_PLACEHOLDER', '{}').format('<hr style="border-top: 1px solid #ccc;">'.join((oddpub_results[doi]['html'], limitation_recognizer_results[doi]['html'], trial_identifier_results[doi]['html'], barzooka_results[doi]['html'], jetfighter_results[doi]['html'], rtransparent_results[doi]['html'], reference_check_results[doi]['html'])))

        tweet_text = generate_tweet_text(doi_to_metadata[doi]['title'],
                                         doi_to_metadata[doi]['url'],
                                         sciscore_results[doi]['is_modeling_paper'],
                                         sum([sr['srList'][0]['sentence'] not in {'not detected.', 'not required.'} for sr in sciscore_results[doi]['raw_json']['rigor-table']['sections'] if sr['title'] in {'Sex as a biological variable', 'Randomization', 'Blinding', 'Power Analysis', 'Cell Line Authentication', 'Ethics'}]),
                                         sum([1 for sr in sciscore_results[doi]['raw_json']['rigor-table']['sections'] if sr['title'] in {'Sex as a biological variable', 'Randomization', 'Blinding', 'Power Analysis', 'Cell Line Authentication', 'Ethics'}]),
                                         sum([sum([len(sr['mentions']) for sr in section['srList']]) for section in sciscore_results[doi]['raw_json']['sections']]),
                                         oddpub_results[doi]['open_code'], oddpub_results[doi]['open_data'],
                                         barzooka_results[doi]['graph_types']['bar'] > 0,
                                         len(limitation_recognizer_results[doi]['sents']) > 0,
                                         len(jetfighter_results[doi]['page_nums']) > 0) #we could add reference check to the list of things we tweet about

        output[doi] = {'url': doi_to_metadata[doi]['url'],
                       'title': doi_to_metadata[doi]['title'],
                       'abstract': doi_to_metadata[doi]['abstract'],
                       'authors': doi_to_metadata[doi]['authors'],
                       'publication_date': doi_to_metadata[doi]['date'].strftime('%m/%d/%Y'),
                       'html_report': html,
                       'tweet_text': tweet_text,
                       'discussion_text': doi_to_text[doi][0],
                       'methods_text': doi_to_text[doi][1],
                       'all_text': doi_to_text[doi][2],
                       'used_full_text_html': doi_to_is_full_text_html[doi],
                       'jet_page_numbers': jetfighter_results[doi]['page_nums'],
                       'limitation_sentences': limitation_recognizer_results[doi]['sents'],
                       'trial_numbers': trial_identifier_results[doi]['trial_identifiers'],
                       'sciscore': sciscore_results[doi]['raw_json'],
                       'is_modeling_paper': sciscore_results[doi]['is_modeling_paper'],
                       'graph_types': barzooka_results[doi]['graph_types'],
                       'is_open_data': oddpub_results[doi]['open_data'],
                       'is_open_code': oddpub_results[doi]['open_code'],
                       'reference_check': reference_check_results[doi]['raw_json'],
                       'coi_statement': rtransparent_results[doi]['coi_statement'],
                       'funding_statement': rtransparent_results[doi]['funding_statement'],
                       'registration_statement': rtransparent_results[doi]['registration_statement']}
    return output
