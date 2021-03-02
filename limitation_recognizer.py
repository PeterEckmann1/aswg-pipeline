import subprocess
import json


def limitation_recognizer():
    output = {}
    subprocess.call(['java', '-jar', 'utils/limitation-recognizer/CombinedPreprintLimitationRecognizer.jar', 'temp/discussion', 'temp/limitations.json'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    results = json.loads(open('temp/limitations.json', 'r', encoding='utf-8').read())
    for result in results:
        if len(result['sents']) == 0:
            statement = 'An explicit section about the limitations of the techniques employed in this study was not found. We encourage authors to address study limitations.'
        else:
            text = ' '.join(result['sents'])
            statement = 'We detected the following sentences addressing limitations in the study:<blockquote>' + text[
                                                                                                                 :1500] + (
                            '...' if len(text) > 1500 else '') + '</blockquote>'
        statement = '<i>Results from <a href="https://academic.oup.com/jamia/article/25/7/855/4990607">LimitationRecognizer</a></i>: ' + statement
        output[result['docId']] = {'html': statement, 'sents': result['sents']}
    return output