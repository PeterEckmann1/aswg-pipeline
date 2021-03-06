import os
import shutil
import subprocess
import time
import random
import csv


time.sleep(10)
while True:
    time.sleep(random.random())
    ids = os.listdir('../papers')
    for id in ids:
        if not os.path.exists('../papers/' + id + '/trial-identifier.html') and os.path.exists('../papers/' + id + '/all.txt') and not os.path.exists('../papers/' + id + '/trial_started'):
            open('../papers/' + id + '/trial_started', 'w').close()
            print('Started processing', id)
            os.mkdir('temp')
            shutil.copyfile('../papers/' + id + '/all.txt', f'temp/10.1101_{id}.txt')
            subprocess.call(['Rscript', 'run.R'])
            shutil.rmtree('temp')
            rows = [['Identifier', 'Status', 'Title']]
            with open('temp.csv', 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                next(f)
                for row in reader:
                    if 'NCT' in row[2] and row[3] == 'TRUE':
                        url = 'https://clinicaltrials.gov/ct2/show/' + row[2]
                        identifier = f'<a href="{url}">{row[2]}</a>'
                    else:
                        identifier = row[2]
                    if row[3] == 'FALSE':
                        rows.append([identifier, 'Trial number did not resolve on <a href="https://clinicaltrials.gov/">clinicaltrials.gov</a>. Is the number correct?', ''])
                    else:
                        try:
                            rows.append([identifier, row[6], row[4][:60] + ('...' if len(row[4]) > 60 else '')])
                        except:
                            print('Trial error, ignoring')
                            pass
            if len(rows) == 1:
                statement = 'No clinical trial numbers were referenced.'
            else:
                table_body = '<table>'
                for row in rows:
                    if 'Trial number did not resolve' in row[1]:
                        table_body += '<tr style="background-color:#FF0000">'
                    else:
                        table_body += '<tr>'
                    for col in row:
                        table_body += f'<td style="min-width:95px; border-right:1px solid lightgray; border-bottom:1px solid lightgray">{col}</td>'
                    table_body += '</tr>'
                table_body += '</table>'
                statement = f'We found the following clinical trial numbers in your paper:<br>{table_body}'
            statement = '<p><i>Results from <a href="https://github.com/bgcarlisle/PreprintScreening">TrialIdentifier</a></i>: {}</p>'.format(statement)
            with open('../papers/' + id + '/trial-identifier_db.txt', 'w', encoding='utf-8') as f:
                f.write(str(rows))
            with open('../papers/' + id + '/trial-identifier.html', 'w', encoding='utf-8') as f:
                f.write(statement)
            os.remove('temp.csv')