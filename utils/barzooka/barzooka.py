import glob
from fastai.vision import *
import urllib3
import re
import pandas as pd
import numpy as np
import warnings


warnings.filterwarnings('ignore')
os.environ['NO_PROXY'] = '127.0.0.1'


class Barzooka(object):
    def __init__(self, model_file='utils/barzooka/barzooka.pkl'):

        super(Barzooka, self).__init__()
        self.learner = load_learner(path='.', file=model_file)
        self.iiif_url = "http://127.0.0.1:8182/iiif/2/" + \
                        "{}:{}.pdf/full/560,560/0/default.png?page={}"
        self.re_pg = re.compile(r'Index: \d+, Size: (\d+)')

    def predict_from_folder(self, pdf_folder, save_filename,
                            iiif_folder='', iiif_mode=False,
                            tmp_folder='./tmp/'):
        if(iiif_folder == '' and iiif_mode):
            raise ValueError("iiif folder argument missing")
        if(tmp_folder == '' and not iiif_mode):
            raise ValueError("tmp folder argument missing")
        if not os.path.exists(tmp_folder) and not iiif_mode:
            os.mkdir(tmp_folder)

        pdf_table = self.__get_pdf_list(pdf_folder, iiif_mode)
        with open(save_filename, "w") as f:
            f.write("bar,pie,hist,bardot,box,dot,violin,paper_id\n")
        for index, row in pdf_table.iterrows():
            paper_id = row['paper_id']
            print(paper_id)
            try:
                if(iiif_mode):
                    barzooka_result = self.__detection_iiif(paper_id, iiif_folder)
                else:
                    barzooka_result = self.predict_from_file(paper_id, tmp_folder)
            except:
                print("Could not screen pdf " + paper_id)

            result_row = pd.DataFrame([barzooka_result])
            result_row.to_csv(save_filename, mode='a', header=False)

    def predict_from_file(self, image_dir):
        img_predict = glob.glob(image_dir)
        images = [open_image(img) for img in img_predict if 'no_barzooka' not in img]
        classes_detected = self.__predict_img_list(images)
        return classes_detected

    def __empty_result(self, paper_id, folder):
        """If pdf with paper_id not available"""
        classes_detected = {
            'bar': 0,
            'pie': 0,
            'hist': 0,
            'bardot': 0,
            'box': 0,
            'dot': 0,
            'violin': 0,
            'paper_id': paper_id.replace("%2b", "/")
        }
        return classes_detected

    def __predict_img_list(self, images):
        """Predicts graph types for each image & returns pages with bar graphs
        """
        page_predictions = np.array([self.__predict_graph_type(images[idx])
                                     for idx in range(0, len(images))])
        # add 1 to page idx such that page counting starts at 1
        bar_pages = np.where(page_predictions == 'bar')[0] + 1
        pie_pages = np.where(page_predictions == 'pie')[0] + 1
        hist_pages = np.where(page_predictions == 'hist')[0] + 1
        bardot_pages = np.where(page_predictions == 'bardot')[0] + 1
        box_pages = np.where(page_predictions == 'box')[0] + 1
        dot_pages = np.where(page_predictions == 'dot')[0] + 1
        violin_pages = np.where(page_predictions == 'violin')[0] + 1
        classes_detected = {
            'bar': len(bar_pages.tolist()),
            'pie': len(pie_pages.tolist()),
            'hist': len(hist_pages.tolist()),
            'bardot': len(bardot_pages.tolist()),
            'box': len(box_pages.tolist()),
            'dot': len(dot_pages.tolist()),
            'violin': len(violin_pages.tolist()),
        }
        return classes_detected

    def __predict_graph_type(self, img):
        """Use fastai model on each image to predict types of pages
        """
        class_names = {
            "0": ["approp"],
            "1": ["bar"],
            "2": ["bardot"],
            "3": ["box"],
            "4": ["dot"],
            "5": ["hist"],
            "6": ["other"],
            "7": ["pie"],
            "8": ["text"],
            "9": ["violin"]
        }
        pred_class, pred_idx, outputs = self.learner.predict(img)
        if pred_idx.sum().tolist() == 0:
            # if there is no predicted class (=no class over threshold)
            # give out class with highest prediction probability
            highest_pred = str(np.argmax(outputs).tolist())
            pred_class = class_names[highest_pred]
        else:
            pred_class = pred_class.obj  # extract class name as text
        return(pred_class)

    def __count_pages(self, paper_id, folder):
        """cantaloupe iiif server returns the highest page index with an error
        if out of range is requested"""
        url = self.iiif_url.format(folder, paper_id, "1000")
        page = self.__req_internal(url)
        try:
            count = self.re_pg.findall(page)[0]
        except:
            count = 0
        return int(count)

    def __req_internal(self, url):
        http = urllib3.PoolManager(cert_reqs='CERT_NONE')
        page = http.request('get', url, timeout=120)
        return page.data.decode('utf-8')