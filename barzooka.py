from utils.barzooka.barzooka import Barzooka
import os
from tqdm import tqdm


b = Barzooka()


def barzooka():
    output = {}
    for safe_doi in tqdm(os.listdir('temp/images'), desc='barzooka'):
        graph_pred = b.predict_from_img_folder(f'temp/images/{safe_doi}/*', pagewise = False)
        output[safe_doi.replace('_', '/')] = {'graph_types': graph_pred}
    return output
