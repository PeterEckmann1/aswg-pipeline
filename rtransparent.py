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
        for line in csv.reader(f, delimiter=' '):
            is_coi, is_fund, is_register = line[3] == 'TRUE', line[5] == 'TRUE', line[7] == 'TRUE'
            output[f_name.replace('_', '/').replace('.txt', '')] = {'coi_statement': is_coi, 'funding_statement': is_fund, 'registration_statement': is_register}
            break
    return output
