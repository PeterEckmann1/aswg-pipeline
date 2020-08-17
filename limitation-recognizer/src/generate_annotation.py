import os
import shutil
import subprocess
import json
import time
import random


time.sleep(20)
while True:
    time.sleep(random.random())
    ids = os.listdir('../papers')
    for id in ids:
        if not os.path.exists('../papers/' + id + '/limitation-recognizer.html') and os.path.exists('../papers/' + id + '/discussion.txt') and not os.path.exists('../papers/' + id + '/limitation_started'):
            open('../papers/' + id + '/limitation_started', 'w').close()
            print('Started processing', id)
            os.mkdir('temp')
            shutil.copyfile('../papers/' + id + '/discussion.txt', 'temp/discussion.txt')
            subprocess.call(['java', '-jar', 'CombinedPreprintLimitationRecognizer.jar', 'temp', 'temp.json'])
            shutil.rmtree('temp')
            with open('temp.json', 'r', encoding='utf-8') as f:
                file_contents = f.read()
            sents = json.loads(file_contents)[0]['sents']
            if len(sents) == 0:
                statement = 'An explicit section about the limitations of the techniques employed in this study was not found. We encourage authors to address study limitations.'
            else:
                statement = 'We detected the following sentences addressing limitations in the study:<blockquote>' + ' '.join(sents) + '</blockquote>'
            statement = '<p><i>Results from <a href="https://academic.oup.com/jamia/article/25/7/855/4990607">LimitationRecognizer</a></i>: ' + statement + '</p>'
            os.remove('temp.json')
            with open('../papers/' + id + '/limitation-recognizer_db.txt', 'w', encoding='utf-8') as f:
                f.write(file_contents)
            with open('../papers/' + id + '/limitation-recognizer.html', 'w', encoding='utf-8') as f:
                f.write(statement)