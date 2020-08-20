import os
import shutil
import time
import barzooka
import random


b = barzooka.Barzooka()


time.sleep(5)
while True:
    time.sleep(random.random())
    ids = os.listdir('../papers')
    for id in ids:
        if not os.path.exists('../papers/' + id + '/barzooka.html') and os.path.exists('../papers/' + id + '/raw.pdf') and not os.path.exists('../papers/' + id + '/barzooka_started'):
            open('../papers/' + id + '/barzooka_started', 'w').close()
            print('Started processing', id)
            os.mkdir('temp')
            bar_pred = b.predict_from_file('../papers/' + id + '/raw.pdf', 'temp')['bar']
            if bar_pred > 0:
                statement = '<p><i>Results from <a href="https://github.com/NicoRiedel/barzooka">Barzooka</a></i>: We found bar graphs of continuous data. We recommend replacing bar graphs with more informative graphics, as many different datasets can lead to the same bar graph. The actual data may suggest different conclusions from the summary statistics. For more information, please see Weissgerber et al (2015).</p>'
            else:
                statement = '<p><i>Results from <a href="https://github.com/NicoRiedel/barzooka">Barzooka</a></i>: We did not find any issues relating to the usage of bar graphs.</p>'
            shutil.rmtree('temp')
            with open('../papers/' + id + '/barzooka_db.txt', 'w', encoding='utf-8') as f:
                f.write(str(bar_pred))
            with open('../papers/' + id + '/barzooka.html', 'w', encoding='utf-8') as f:
                f.write(statement)