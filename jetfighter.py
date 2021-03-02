import os
from utils.jetfighter import detect_cmap
from tqdm import tqdm
from multiprocessing import Pool


def run_jetfighter(args):
    image_dir = args['dir'] + args['safe_doi']
    try:
        has_rainbow = detect_cmap.detect_cmap(image_dir + '/*')
    except (KeyError, ValueError):
        return args['safe_doi'].replace('_', '/'), {'html': '<p><i>Results from <a href="https://elifesciences.org/labs/c2292989/jetfighter-towards-figure-accuracy-and-accessibility">JetFighter</a></i>: We did not find any issues relating to colormaps.</p>', 'page_nums': []}
    fig_num_to_page_num = {}
    for f_name in os.listdir(image_dir):
        _, page_num, fig_num = f_name.split('-')
        fig_num_to_page_num[int(fig_num.split('.')[0])] = int(page_num)
    has_rainbow = [fig_num_to_page_num[fig_num] for fig_num in has_rainbow]
    has_rainbow_no_dup = list(set(has_rainbow))
    if not has_rainbow_no_dup:
        html = 'We did not find any issues relating to colormaps.'
    elif len(has_rainbow_no_dup) == 1:
        html = f'Please consider improving the rainbow (“jet”) colormap(s) used on page {has_rainbow_no_dup[0]}. At least one figure is not accessible to readers with colorblindness and/or is not true to the data, i.e. not perceptually uniform.'
    else:
        html = f"Please consider improving the rainbow (“jet”) colormap(s) used on pages {', '.join([str(num) for num in has_rainbow_no_dup[:-1]]) + ' and ' + str(has_rainbow_no_dup[-1])}. At least one figure is not accessible to readers with colorblindness and/or is not true to the data, i.e. not perceptually uniform."
    html = f'<p><i>Results from <a href="https://elifesciences.org/labs/c2292989/jetfighter-towards-figure-accuracy-and-accessibility">JetFighter</a></i>: {html}</p>'
    return args['safe_doi'].replace('_', '/'), {'html': html, 'page_nums': has_rainbow}


def jetfighter(use_scaled, workers):
    images = os.listdir('temp/images_scaled') if use_scaled else os.listdir('temp/images')
    all_args = []
    for safe_doi in images:
        all_args.append({'dir': ('temp/images_scaled/' if use_scaled else 'temp/images/'), 'safe_doi': safe_doi})
    with Pool(workers) as pool:
        results = list(tqdm(pool.imap_unordered(run_jetfighter, all_args), total=len(all_args), desc='jetfighter'))
    output = {}
    for doi, result in results:
        output[doi] = result
    return output