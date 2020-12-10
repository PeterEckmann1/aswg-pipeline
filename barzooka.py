from utils.barzooka.barzooka import Barzooka
import os
from tqdm import tqdm


b = Barzooka()


def barzooka():
    output = {}
    for safe_doi in tqdm(os.listdir('temp/images'), desc='barzooka'):
        bar_pred = b.predict_from_file(f'temp/images/{safe_doi}/*')
        if bar_pred['bar'] > 0:
            statement = '<p><i>Results from <a href="https://github.com/NicoRiedel/barzooka">Barzooka</a></i>: We found bar graphs of continuous data. We recommend replacing bar graphs with more informative graphics, as many different datasets can lead to the same bar graph. The actual data may suggest different conclusions from the summary statistics. For more information, please see Weissgerber et al (2015).</p>'
        else:
            statement = '<p><i>Results from <a href="https://github.com/NicoRiedel/barzooka">Barzooka</a></i>: We did not find any issues relating to the usage of bar graphs.</p>'
        output[safe_doi.replace('_', '/')] = {'html': statement, 'graph_types': bar_pred}
    return output
