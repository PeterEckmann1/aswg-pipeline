import subprocess
import json


def limitation_recognizer():
    output = {}
    subprocess.call(['java', '-jar', 'utils/limitation-recognizer/CombinedPreprintLimitationRecognizer.jar', 'temp/discussion', 'temp/limitations.json'])#, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    results = json.loads(open('temp/limitations.json', 'r', encoding='utf-8').read())
    for result in results:
        output[result['docId']] = {'sents': result['sents']}
    return output
