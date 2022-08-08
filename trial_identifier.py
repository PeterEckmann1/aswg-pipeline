import subprocess
import csv


def trial_identifier(dois):
    subprocess.call(['Rscript', 'utils/trial-identifier/identifier.R'], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
    output = {}
    current_doi = ''
    with open('temp/trials.csv', 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(f)
        for row in reader:
            if current_doi != row[0]:
                current_doi = row[0]
                if current_doi.replace('_', '/') not in output:
                    output[current_doi.replace('_', '/')] = {'trial_identifiers': []}
            try:
                output[current_doi.replace('_', '/')]['trial_identifiers'].append({'identifier': row[2], 'link':('https://clinicaltrials.gov/ct2/show/' + row[2] if 'NCT' in row[2] else None), 'resolved': row[3] == 'TRUE', 'title': row[4], 'status': row[6]})
            except IndexError:
                output[current_doi.replace('_', '/')]['trial_identifiers'].append({'identifier': row[2], 'link': None, 'resolved': row[3] == 'TRUE', 'title': 'NA', 'status': 'NA'})
    for doi in dois:
        if doi not in output:
            output[doi] = {'trial_identifiers': []}
    return output
