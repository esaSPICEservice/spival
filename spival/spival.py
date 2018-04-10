#!/usr/bin/env python3

from spiops import spiops

import nbformat as nbf
from nbconvert.preprocessors import ExecutePreprocessor
from nbconvert import HTMLExporter

def spival(config):

    with open('em16_ops.tm', 'w') as tm:

        with open(config['skd_path']+ '/mk/' + config['mk'], 'r') as f:
            for line in f:
                if "'..'" in line:
                    line = line.replace("'..'",
                                        "'"+config['skd_path']+"'")
                tm.write(line)


    mk = '"em16_ops.tm"'


    nb = nbf.v4.new_notebook()

    text = "# My first automatic Jupyter Notebook\n" + \
           "This is an auto-generated notebook."

    nb['cells'] = [nbf.v4.new_markdown_cell(text)]

    code = "import spiops as spiops \n" + \
           "spiops.load({})\n".format(mk) + \
           "start_time = {}\n".format('"2018-03-12T00:00:00"') + \
           "finish_time = {}\n".format('"2018-03-15T00:00:00"') + \
           "interval = spiops.TimeWindow(start_time, finish_time,resolution=60)\n" + \
           "mars = spiops.Target('MARS', time=interval, frame='IAU_MARS')\n" + \
           "tgo = spiops.Observer('TGO', time=interval, target=mars)"

    nb['cells'] += [nbf.v4.new_code_cell(code)]


    text = "| This | is   |\n" + \
           "|------|------|\n" + \
           "|   a  | table|\n"

    code = "tgo.Plot('distance', notebook=True)\n" + \
           "tgo.Plot('zaxis_target_angle', notebook=True)"

    nb['cells'] += [nbf.v4.new_code_cell(code)]

    nbf.write(nb, 'test.ipynb')

    ep = ExecutePreprocessor(timeout=600, kernel_name='python3')

    ep.preprocess(nb, {'metadata': {'path': ''}})

    nbf.write(nb, 'test_executed.ipynb')


    html_exporter = HTMLExporter()
    html_exporter.template_file = 'full'

    (body, resources) = html_exporter.from_notebook_node(nb)

    with open('test_exectued.html', 'w') as h:
        for element in body:
            h.write(element)

#    spiops.load('em16_ops.tm')
#
#    spk_list = []
#
#    with open('em16_ops.tm', 'r') as f:
#        for line in f:
#            if '.bsp' in line.lower():
#                spk_list.append(line.split('/')[-1].strip()[:-1])#
#
#    for spk in spk_list:
#        test_cov_spk(spk=config['skd_path']+'/spk/'+spk)

    return


#def test_cov_spk(spk):
#
#    cov = spiops.cov_spk_ker(spk=spk,
#                             time_format='UTC')
#
#    print('Coverage for',spk)
#    index = 0
#    for element in cov[0]:
#        print(element, cov[1][index])
#        index += 1
#
#    return