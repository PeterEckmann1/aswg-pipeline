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
        if doi in output:
            table_body = '<table><td style="min-width:95px; border-right:1px solid lightgray; border-bottom:1px solid lightgray">Identifier</td><td style="min-width:95px; border-right:1px solid lightgray; border-bottom:1px solid lightgray">Status</td><td style="min-width:95px; border-right:1px solid lightgray; border-bottom:1px solid lightgray">Title</td></tr>'
            for identifier in output[doi]['trial_identifiers']:
                if identifier['resolved'] or 'ISRCTN' in identifier['identifier']:
                    table_body += '<tr>'
                else:
                    table_body += '<tr style="background-color:#FF0000">'
                table_body += '<td style="min-width:95px; border-right:1px solid lightgray; border-bottom:1px solid lightgray">' + \
                              ('<a href="{}">{}</a>'.format(identifier['link'], identifier['identifier']) if identifier['link'] else identifier['identifier']) + '</td><td style="min-width:95px; border-right:1px solid lightgray; border-bottom:1px solid lightgray">' + \
                              (identifier['status'] if (identifier['resolved'] or 'ISRCTN' in identifier['identifier']) else 'Trial number did not resolve on <a href="https://clinicaltrials.gov/">clinicaltrials.gov</a>. Is the number correct?') + '</td><td style="min-width:95px; border-right:1px solid lightgray; border-bottom:1px solid lightgray">' + \
                              identifier['title'][:60] + ('…' if len(identifier['title']) > 60 else '') + '</td></tr>'
            output[doi]['html'] = '<p><i>Results from <a href="https://github.com/bgcarlisle/PreprintScreening">TrialIdentifier</a></i>: We found the following clinical trial numbers in your paper:<br>' + table_body + '</table></p>'
        else:
            output[doi] = {'html': '<p><i>Results from <a href="https://github.com/bgcarlisle/PreprintScreening">TrialIdentifier</a></i>: No clinical trial numbers were referenced.</p>', 'trial_identifiers': []}
    return output
