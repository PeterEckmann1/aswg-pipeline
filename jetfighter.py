import os
from utils.jetfighter import detect_cmap
from tqdm import tqdm
from multiprocessing import Pool


def run_jetfighter(args):
    image_dir = args['dir'] + args['safe_doi']
    try:
        has_rainbow = detect_cmap.detect_cmap(image_dir + '/*')
    except (KeyError, ValueError):
        return args['safe_doi'].replace('_', '/'), {'page_nums': []}
    fig_num_to_page_num = {}
    for f_name in os.listdir(image_dir):
        _, page_num, fig_num = f_name.split('-')
        fig_num_to_page_num[int(fig_num.split('.')[0])] = int(page_num)
    has_rainbow = [fig_num_to_page_num[fig_num] for fig_num in has_rainbow]
    return args['safe_doi'].replace('_', '/'), {'page_nums': list(set(has_rainbow))}


def jetfighter(use_scaled, workers):
    images = os.listdir('temp/images_scaled') if use_scaled else os.listdir('temp/images')
    all_args = []
    for safe_doi in images:
        all_args.append({'dir': ('temp/images_scaled/' if use_scaled else 'temp/images/'), 'safe_doi': safe_doi})
    if workers == 1:
        results = [run_jetfighter(all_args[0])]
    else:
        with Pool(workers) as pool:
            results = list(tqdm(pool.imap_unordered(run_jetfighter, all_args), total=len(all_args), desc='jetfighter'))
    output = {}
    for doi, result in results:
        output[doi] = result
    return output