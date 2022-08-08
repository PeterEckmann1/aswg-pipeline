import subprocess
import csv


def oddpub():
    output = {}
    subprocess.call(['Rscript', 'utils/oddpub/oddpub.R', 'temp/all_text/', 'temp/oddpub.csv'])#, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
    f = open('temp/oddpub.csv', 'r')
    next(f)
    for row in csv.reader(f, delimiter=' '):
        import sys
        print(row, file=sys.stderr)
        doi = row[1].replace('"', '').replace('.txt', '').replace('_', '/')
        open_data = row[2] == 'TRUE'
        open_code = row[4] == 'TRUE'
        output[doi] = {'open_code': open_code, 'open_data': open_data, 'open_data_statement': row[5], 'open_code_statemenent': row[6]}
    return output