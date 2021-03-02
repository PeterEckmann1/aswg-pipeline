import subprocess


def oddpub():
    output = {}
    subprocess.call(['Rscript', 'utils/oddpub/oddpub.R', 'temp/all_text/', 'temp/oddpub.csv'], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
    f = open('temp/oddpub.csv', 'r')
    next(f)
    for line in f:
        doi = line.split()[1].replace('"', '').replace('.txt', '').replace('_', '/')
        open_data = None
        open_code = None
        for col in line.split():
            if col in ['FALSE', 'TRUE']:
                if open_data is None:
                    open_data = col == 'TRUE'
                else:
                    open_code = col == 'TRUE'
                    break
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
        output[doi] = {'html': statement, 'open_code': open_code, 'open_data': open_data}
    return output