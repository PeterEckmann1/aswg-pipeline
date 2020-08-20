import os
import shutil
import subprocess
import json
import time
import detect_cmap
import random


time.sleep(5)
while True:
    time.sleep(random.random())
    ids = os.listdir('../papers')
    for id in ids:
        if not os.path.exists('../papers/' + id + '/jetfighter.html') and os.path.exists('../papers/' + id + '/raw.pdf') and not os.path.exists('../papers/' + id + '/jetfighter_started'):
            open('../papers/' + id + '/jetfighter_started', 'w').close()
            print('Started processing', id)
            subprocess.call(['pdfimages', '-png', '-p', '../papers/' + id + '/raw.pdf', 'pdf_imgs/img'])
            try:
                has_rainbow = detect_cmap.detect_cmap('pdf_imgs/img*')
            except:
                print('No images found in', id)
                has_rainbow = []
            fig_num_to_page_num = {}
            for f_name in os.listdir('pdf_imgs'):
                _, page_num, fig_num = f_name.split('-')
                fig_num_to_page_num[int(fig_num.split('.')[0])] = int(page_num)
                os.remove('pdf_imgs/' + f_name)
            has_rainbow = [str(fig_num_to_page_num[fig_num]) for fig_num in has_rainbow]
            if has_rainbow == []:
                statement = 'We did not find any issues relating to colormaps.'
            elif len(has_rainbow) == 1:
                statement = 'Please consider improving the rainbow (“jet”) colormap used on page {}. At least one figure is not accessible to readers with colorblindness and/or is not true to the data, i.e. not perceptually uniform.'.format(has_rainbow[0])
            else:
                statement = 'Please consider improving the rainbow (“jet”) colormap used on pages {}. At least one figure is not accessible to readers with colorblindness and/or is not true to the data, i.e. not perceptually uniform.'.format(', '.join(has_rainbow[:-1]) + ' and ' + has_rainbow[-1])
            statement = '<p><i>Results from <a href="https://elifesciences.org/labs/c2292989/jetfighter-towards-figure-accuracy-and-accessibility">JetFighter</a></i>: {}</p>'.format(statement)
            with open('../papers/' + id + '/jetfighter_db.txt', 'w', encoding='utf-8') as f:
                f.write(','.join(has_rainbow))
            with open('../papers/' + id + '/jetfighter.html', 'w', encoding='utf-8') as f:
                f.write(statement)