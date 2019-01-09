#!/usr/bin/env python3

import glob
from spiops import utils
import shutil
import os
import nbformat as nbf
from nbconvert.preprocessors import ExecutePreprocessor
from nbconvert import HTMLExporter

def jupyter_writer(config):

    mk = config['mk']

    with open(mk, 'w') as tm:

        with open(config['skd_path']+ '/mk/' + config['mk'], 'r') as f:
            for line in f:
                if "'..'" in line:
                    line = line.replace("'..'",
                                        "'"+config['skd_path']+"'")
                tm.write(line)

                if 'SKD_VERSION' in line:
                    skd_version = line.split("'")[1]
                else:
                    skd_version = 'None'

    nb = nbf.v4.new_notebook()

    text = "# ExoMars2016 SPICE Kernel Dataset Status\n" + \
           "Last updated on {} by Marc Costa Sitja (ESAC/ESA)".format('10 Apr 2018') + \
           "SKD version: {}\n".format(skd_version) + \
           "\n" + \
           "## Startup and Coverage\n"

    nb['cells'] = [nbf.v4.new_markdown_cell(text)]

    code = "import spiops as spiops \n" + \
           "spiops.load({})\n".format('"'+mk+'"') + \
           "start_time = {}\n".format('"2018-03-12T00:00:00"') + \
           "finish_time = {}\n".format('"2018-03-15T00:00:00"') + \
           "interval = spiops.TimeWindow(start_time, finish_time,resolution=60)\n" + \
           "mars = spiops.Target('MARS', time=interval, frame='IAU_MARS')\n" + \
           "tgo = spiops.Observer('TGO', time=interval, target=mars)"

    nb['cells'] += [nbf.v4.new_code_cell(code)]

    text = "## Geometry Plots\n" + \
           "\n" + \
           "TGO-Mars Distance in Km \n"

    nb['cells'] += [nbf.v4.new_markdown_cell(text)]

    text = "| This | is   |\n" + \
           "|------|------|\n" + \
           "|   a  | table|\n"

    code = "tgo.Plot('distance', notebook=True)\n" + \
           "tgo.Plot('zaxis_target_angle', notebook=True)"

    nb['cells'] += [nbf.v4.new_code_cell(code)]



    ep = ExecutePreprocessor(timeout=600, kernel_name='python3')

    ep.preprocess(nb, {'metadata': {'path': ''}})

    nbf.write(nb, mk.split('.')[0] + '.ipynb')


    html_exporter = HTMLExporter()
    html_exporter.template_file = 'full'

    (body, resources) = html_exporter.from_notebook_node(nb)

    with open(mk.split('.')[0] +'.html', 'w') as h:
        for element in body:
            h.write(element)

    shutil.move(mk.split('.')[0] +'.html', os.path.join(config['html_path'],
                mk.split('.')[0]+'.html'))


    return

def skd_check():

    cwd = os.getcwd()
    mks_in_dir = glob.glob('*.tm')
    mks_in_dir += glob.glob('*.TM')

    for mk_in_dir in mks_in_dir:
        output = utils.brief(os.path.join(cwd,mk_in_dir))
        print(output)
        if 'SPICE(' in output:
            raise ValueError('BRIEF utility could not run')

    return