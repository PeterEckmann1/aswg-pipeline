import subprocess
import os
import csv
import sys

csv_size = sys.maxsize
while True:
    try:
        csv.field_size_limit(csv_size)
        break
    except:
        csv_size = int(csv_size / 10)


#todo may have to add additional data from the website, especially medrxiv
#todo footnotes not picked up? make sure to actually verify this tool
def rtransparent():
    output = {}
    for f_name in os.listdir('temp/all_text'):
        subprocess.call(['Rscript', 'utils/rtransparent/rtransparent.R', 'temp/all_text/' + f_name, 'temp/rtransparent.csv'])
        f = open('temp/rtransparent.csv', 'r')
        next(f)
        statement = ''
        for line in csv.reader(f, delimiter=' '):
            is_coi, is_fund, is_register = line[3] == 'TRUE', line[5] == 'TRUE', line[7] == 'TRUE'
            if is_coi:
                statement += '<li>Thank you for including a conflict of interest statement. Authors are encouraged to include this statement when submitting to a journal.</li>'
            else:
                statement += '<li>No conflict of interest statement was detected. If there are no conflicts, we encourage authors to explicit state so.</li>'

            if is_fund:
                statement += '<li>Thank you for including a funding statement. Authors are encouraged to include this statement when submitting to a journal.</li>'
            else:
                statement += '<li>No funding statement was detected.</li>'

            if is_register:
                statement += '<li>Thank you for including a protocol registration statement.</li>'
            else:
                statement += '<li>No protocol registration statement was detected.</li>'
            output[f_name.replace('_', '/').replace('.txt', '')] = {'html': f'<i>Results from <a href="https://www.biorxiv.org/content/10.1101/2020.10.30.361618v1">rtransparent</a></i>: <ul>{statement}</ul>', 'coi_statement': is_coi, 'funding_statement': is_fund, 'registration_statement': is_register}
            break
    return output
