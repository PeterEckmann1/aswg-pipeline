import os
import shutil
import subprocess
import time
import random


time.sleep(20)
while True:
    time.sleep(random.random())
    ids = os.listdir('../papers')
    for id in ids:
        if not os.path.exists('../papers/' + id + '/oddpub.html') and os.path.exists('../papers/' + id + '/all.txt') and not os.path.exists('../papers/' + id + '/oddpub_started'):
            open('../papers/' + id + '/oddpub_started', 'w').close()
            print('Started processing', id)
            os.mkdir('temp')
            shutil.copyfile('../papers/' + id + '/all.txt', 'temp/all.txt')
            print('pog')
            subprocess.call(['Rscript', 'run.R'])
            print('U')
            shutil.rmtree('temp')
            with open('temp.csv', 'r', encoding='utf-8') as f:
                line = f.readlines()[1].split()
                open_data, open_code = line[2] == 'TRUE', line[3] == 'TRUE'
            if open_data:
                if open_code:
                    statement = 'Thank you for sharing your code and data.'
                else:
                    statement = 'Thank you for sharing your data.'
            else:
                if open_code:
                    statement = 'Thank you for sharing your code.'
                else:
                    statement = 'We did not detect open data. We also did not detect open code. Researchers are encouraged to share open data when possible (see <a href="http://blogs.nature.com/naturejobs/2017/06/19/ask-not-what-you-can-do-for-open-data-ask-what-open-data-can-do-for-you/">Nature blog</a>).'
            statement = '<p><i>Results from <a href="https://www.biorxiv.org/content/10.1101/2020.05.11.088021v1">OddPub</a></i>: {}</p>'.format(statement)
            with open('../papers/' + id + '/oddpub_db.txt', 'w', encoding='utf-8') as f:
                f.write(str(open_code) + ',' + str(open_data))
            with open('../papers/' + id + '/oddpub.html', 'w', encoding='utf-8') as f:
                f.write(statement)