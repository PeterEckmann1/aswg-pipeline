import os
import re
import pickle
import csv
import random
import unicodedata
from collections import Counter
from sklearn import svm
from sklearn.datasets import load_svmlight_file
import sklearn.metrics
from joblib import dump, load
from os.path import isfile, join


class Instance(object):
    def __init__(self, id, instance_id, content, label=None):
        self.id = id
        self.instance_id = instance_id
        self.content = content
        self.label = label
        self.prediction = None

    def to_svm(self, vocab):
        s = '0 '
        if self.label is not None:
            s = '1 ' if self.label == 1 else '-1 '
        offset = 0
        ft = Counter()
        for token in self.content.split():
            token = token.lower() if vocab.lowercase else token
            ft[token] += 1
        wids = sorted(list(set(vocab.get_id(word) for word in ft.keys())))
        if wids and wids[0] == -1:
            wids.pop(0)
        for wid in wids:
            s += '{:d}:1 '.format(wid + offset)
        return s


class Vocabulary(object):
    def __init__(self, vocabulary=dict(), lowercase=False):
        self.vocabulary = vocabulary
        self.lowercase = lowercase

    def prepare(self, instances, lowercase=False):
        self.lowercase = lowercase
        ft = Counter()
        for instance in instances:
            for token in instance.content.split():
                token = token.lower() if lowercase else token
                ft[token] += 1
        for word in sorted(ft.keys()):
            self.vocabulary[word] = len(self.vocabulary)

    def get_id(self, word):
        if word not in self.vocabulary:
            return -1
        return self.vocabulary.get(word)

    def save(self, ser_file):
        contents = {'vocabulary': self.vocabulary,
                    'lowercase': self.lowercase}
        with open(ser_file, "wb") as f:
            pickle.dump(contents, f)

    @classmethod
    def from_serializable(cls, ser_file):
        with open(ser_file, "rb") as f:
            contents = pickle.load(f)
            return cls(**contents)

    def __len__(self):
        return len(self.vocabulary)

    def __str__(self):
        return "<Vocabulary(size={},lowercase={}>".format(len(self),
                                                          self.lowercase)


def load_as_string(text_file):
    with open(text_file, 'r', encoding='utf-8') as f:
        data = f.read().replace('\n', '')
    return data


def strip_accents(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s)
                   if unicodedata.category(c) != 'Mn')


def load_covid19_annotated_data(label_csv_file, paper_dir, modeling=True):
    lines = []
    with open(label_csv_file, 'r') as f:
        reader = csv.reader(f, delimiter=',')
        count = 0
        for line in reader:
            lines.append(line)
            count += 0
            # only first 199 entries are annotated
            if count >= 200:
                break
    lines.pop(0)  # skip header
    doi_2_label = dict()
    for line in lines:
        doi = line[0]
        idx = 2 if modeling else 3
        label = line[idx]
        if len(label) == 0 or label.lower() == 'withdrawn':
            continue
        doi = doi.replace('/', '_')
        doi_2_label[doi] = label
    print("doi_2_label size: {}".format(len(doi_2_label)))
    files = [f for f in os.listdir(paper_dir) if isfile(join(paper_dir, f))]
    count = 0
    instances = list()
    for f in files:
        prefix = re.sub(r'\.txt$', '', f)
        if prefix in doi_2_label:
            label = doi_2_label[prefix]
            content = load_as_string(join(paper_dir, f))
            content = strip_accents(content)
            inst = Instance(str(count), prefix, content, int(label))
            instances.append(inst)
            count += 1
    return instances


def prep_train_test_set(instances, test_frac=0.2):
    instances = list(instances)
    random.shuffle(instances)
    test_size = int(len(instances) * test_frac)
    test_list = instances[:test_size]
    train_list = instances[test_size:]
    return (train_list, test_list)


def prep_train_test_instances(label_csv_file, paper_dir, train_file,
                              test_file=None, test_frac=0.):
    instances = load_covid19_annotated_data(label_csv_file, paper_dir)
    if test_frac > 0:
        train_list, test_list = prep_train_test_set(instances,
                                                    test_frac=test_frac)
    else:
        train_list = instances
        test_list = None
    print('# instances:', len(instances))
    vocab = Vocabulary()
    vocab.prepare(train_list, lowercase=True)
    print('vocab size:', len(vocab.vocabulary))
    vocab.save('pt_vocab.ser')
    print(vocab)
    save_svmlight(train_list, vocab, train_file)
    print('wrote ', train_file)
    if test_list:
        save_svmlight(test_list, vocab, test_file)
        print('wrote ', test_file)


def save_svmlight(instances, vocab, out_file):
    with open(out_file, 'w') as f:
        for instance in instances:
            f.write(instance.to_svm(vocab))
            f.write("\n")


def train_model(train_data_file, test_data_file):
    X, y = load_svmlight_file(train_data_file, zero_based=True)
    print('train X.shape=', X.shape)
    clf = svm.SVC(kernel='linear', verbose=True)
    clf.fit(X, y)
    print("")
    print("finished training")
    dump(clf, 'pt_model.joblib')
    print("saved model to: pt_model.joblib")
    if test_data_file:
        n_features = X.shape[1]
        X, y_true = load_svmlight_file(test_data_file,
                                       zero_based=True,
                                       n_features=n_features)
        preds = clf.predict(X)
        p, r, f, _ = sklearn.metrics.precision_recall_fscore_support(
             y_pred=preds, y_true=y_true)
        print("")
        f1 = f[1] * 100
        p = p[1] * 100
        r = r[1] * 100
        print("P:{:.1f} R:{:.1f} f1:{:.1f}".format(p, r, f1))


def predict_if_model_paper(methods_content, threshold=0.5):
    import tempfile
    content = strip_accents(methods_content)
    instances = [Instance(0, 'test', content, 0)]
    clf = load('utils/sciscore/pt_model.joblib')
    vocab = Vocabulary.from_serializable('utils/sciscore/pt_vocab.ser')
    fp, pred_file = tempfile.mkstemp(suffix=".dat")
    os.close(fp)
    save_svmlight(instances, vocab, pred_file)
    X, _ = load_svmlight_file(pred_file, zero_based=True,
                              n_features=len(vocab))
    preds = clf.predict(X)
    os.remove(pred_file)
    return preds[0] > threshold


def test_prediction():
    paper_dir = '/home/bozyurt/dev/java/sciscore-learn/data/covid_classify/annotated/papers'
    content = load_as_string(paper_dir + '/10.1101_2020.03.27.20044891.txt')
    print("Modeling paper:", predict_if_model_paper(content))


if __name__ == '__main__':
    label_csv_file = 'type_classifier/covid_modeling.csv'
    paper_dir = 'type_classifier/papers'
    train_file = 'type_classifier/pp_train.dat'
    test_file = 'type_classifier/pp_test.dat'
    # prep_train_test_instances(label_csv_file, paper_dir, train_file, test_file,
    #                          test_frac=0.1)
    # train_model(train_file, test_file)
    # train full model
    prep_train_test_instances(label_csv_file, paper_dir, train_file)
    train_model(train_file, None)
    # test_prediction()
