from multiprocessing import Pool
import requests
import pickle
import time


def get_url(url):
    try:
        return requests.get(url)
    except:
        print('failed, trying')
        time.sleep(5)
        try:
            return requests.get(url)
        except:
            print('failed, trying again')
            time.sleep(15)
            return requests.get(url)


if __name__ == '__main__':
    with Pool(60) as pool:
        objs = pool.map(get_url, pickle.load(open('urls.pickle', 'rb')))
    pickle.dump(objs, open('url_responses.pickle', 'wb'))