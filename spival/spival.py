#!/usr/bin/env python3

import glob
import os
import datetime
import shutil
import git

import spiops

from .utils import utils

def write_ExoMars2016(config):

    root_dir = os.path.dirname(__file__)

    repo = git.Repo(config['skd_path'][:-7])
    tags = repo.tags

    #
    # Set the replacements for the Notebook template
    #
    replacements = {}
    replacements['metakernel'] = config['skd_path']+ '/mk/' + config['mk']


    spiops.load(replacements['metakernel'])


    with open(replacements['metakernel'], 'r') as f:
        for line in f:
            if 'SKD_VERSION' in line:
                replacements['skd_version'] = line.split("'")[1]
                break
            else:
                replacements['skd_version'] = 'N/A'

        #
        # We obtain the predicted and the measured CKs
        #
    replacements['predicted_ck'] = spiops.utils.get_latest_kernel('ck',config['skd_path'],'em16_tgo_sc_fsp_*_s????????_v??.bc')
    replacements['measured_ck'] = spiops.utils.get_latest_kernel('ck', config['skd_path'],'em16_tgo_sc_ssm_*_s????????_v??.bc')

        #
        # We obtain today's date
        #
    now = datetime.datetime.now()
    replacements['current_time'] = now.strftime("%Y-%m-%dT%H:%M:%S")

    boundary  = spiops.cov_ck_ker(config['skd_path']+ '/ck/' + replacements['measured_ck'], 'TGO_SPACECRAFT', time_format='UTC')

    mes_finish_time = boundary[-1][:-4]
    mes_start_date = datetime.datetime.strptime(mes_finish_time, '%Y-%m-%dT%H:%M:%S')
    mes_start_date = mes_start_date - datetime.timedelta(days=7)
    mes_start_time = mes_start_date.strftime("%Y-%m-%dT%H:%M:%S")

    #
    # We obtain the dates from the Tags
    #
    start_date = str(tags[-2]).split('_')[1]
    start_time = '{}-{}-{}T00:00:00'.format(start_date[0:4],start_date[4:6],start_date[6:8])

    finish_date = str(tags[-1]).split('_')[1]
    finish_time = '{}-{}-{}T00:00:00'.format(start_date[0:4],start_date[4:6],start_date[6:8])

    index = -2
    while start_time == finish_time:
        start_date = str(tags[index]).split('_')[1]
        start_time = '{}-{}-{}T00:00:00'.format(start_date[0:4],
                                                start_date[4:6],
                                                start_date[6:8])
        index -= 1


    replacements['start_time'] = start_time
    replacements['finish_time'] = finish_time

    replacements['start_time_measured'] = mes_start_time
    replacements['finish_time_measured'] = mes_finish_time

    template = root_dir + '/notebooks/ExoMars2016.ipynb'

    #
    # Notebook for Jenkins and HTML publication
    #
    output = 'ExoMars2016_' + replacements['skd_version'] + '.ipynb'
    replacements['skd_path'] = config['skd_path']
    utils.fill_template(template, output, replacements)
    shutil.move(output, os.path.join(config['notebooks_path'],output))

    #
    # Notebook for the GitHub Laboratory
    #
    output = 'index.ipynb'
    replacements['metakernel'] = config['github_skd_path'] + '/mk/' + config['mk']
    replacements['skd_path'] = config['github_skd_path']
    utils.fill_template(template, output, replacements)
    shutil.move(output, os.path.join(config['notebooks_path'],output))

    #
    # Update the HTMLs
    #
    update_html(config)

    return


def write_BepiColombo(config):

    root_dir = os.path.dirname(__file__)

    repo = git.Repo(config['skd_path'][:-7])
    tags = repo.tags

    #
    # Set the replacements for the Notebook template
    #
    replacements = {}
    replacements['metakernel'] = config['skd_path']+ '/mk/' + config['mk']


    spiops.load(replacements['metakernel'])


    with open(replacements['metakernel'], 'r') as f:
        for line in f:
            if 'SKD_VERSION' in line:
                replacements['skd_version'] = line.split("'")[1]
                break
            else:
                replacements['skd_version'] = 'N/A'

        #
        # We obtain the predicted and the measured CKs
        #
    replacements['predicted_ck'] = spiops.utils.get_latest_kernel('ck',config['skd_path'],'bc_mpo_sc_fsp_*_f????????_v??.bc')
    replacements['measured_ck'] = spiops.utils.get_latest_kernel('ck', config['skd_path'],'bc_mpo_sc_scm_*_s????????_v??.bc')

        #
        # We obtain today's date
        #
    now = datetime.datetime.now()
    replacements['current_time'] = now.strftime("%Y-%m-%dT%H:%M:%S")

    boundary  = spiops.cov_ck_ker(config['skd_path']+ '/ck/' + replacements['measured_ck'], 'MPO_SPACECRAFT', time_format='UTC')

    mes_finish_time = boundary[-1][:-4]
    mes_start_date = datetime.datetime.strptime(mes_finish_time, '%Y-%m-%dT%H:%M:%S')
    mes_start_date = mes_start_date - datetime.timedelta(days=7)
    mes_start_time = mes_start_date.strftime("%Y-%m-%dT%H:%M:%S")

    #
    # We obtain the dates from the Tags
    #
    start_date = str(tags[-2]).split('_')[1]
    start_time = '{}-{}-{}T00:00:00'.format(start_date[0:4],start_date[4:6],start_date[6:8])

    finish_date = str(tags[-1]).split('_')[1]
    finish_time = '{}-{}-{}T00:00:00'.format(start_date[0:4],start_date[4:6],start_date[6:8])

    index = -2
    while start_time == finish_time:
        start_date = str(tags[index]).split('_')[1]
        start_time = '{}-{}-{}T00:00:00'.format(start_date[0:4],
                                                start_date[4:6],
                                                start_date[6:8])
        index -= 1


    replacements['start_time'] = start_time
    replacements['finish_time'] = finish_time

    replacements['start_time_measured'] = mes_start_time
    replacements['finish_time_measured'] = mes_finish_time

    template = root_dir + '/notebooks/BEPICOLOMBO.ipynb'

    #
    # Notebook for Jenkins and HTML publication
    #
    output = 'BEPICOLOMBO_' + replacements['skd_version'] + '.ipynb'
    replacements['skd_path'] = config['skd_path']
    utils.fill_template(template, output, replacements)
    shutil.move(output, os.path.join(config['notebooks_path'],output))

    #
    # Notebook for the GitHub Laboratory
    #
    output = 'index.ipynb'
    replacements['metakernel'] = config['github_skd_path'] + '/mk/' + config['mk']
    replacements['skd_path'] = config['github_skd_path']
    utils.fill_template(template, output, replacements)
    shutil.move(output, os.path.join(config['notebooks_path'],output))

    #
    # Update the HTMLs
    #
    update_html(config)

    return


def write_MarsExpress(config):

    root_dir = os.path.dirname(__file__)

    repo = git.Repo(config['skd_path'][:-7])
    tags = repo.tags

    #
    # Set the replacements for the Notebook template
    #
    replacements = {}
    replacements['metakernel'] = config['skd_path']+ '/mk/' + config['mk']


    spiops.load(replacements['metakernel'])


    with open(replacements['metakernel'], 'r') as f:
        for line in f:
            if 'SKD_VERSION' in line:
                replacements['skd_version'] = line.split("'")[1]
                break
            else:
                replacements['skd_version'] = 'N/A'

        #
        # We obtain today's date
        #
    now = datetime.datetime.now()
    replacements['current_time'] = now.strftime("%Y-%m-%dT%H:%M:%S")

    #
    # We obtain the dates from the Tags
    #
    start_date = str(tags[-2]).split('_')[1]
    start_time = '{}-{}-{}T00:00:00'.format(start_date[0:4],start_date[4:6],start_date[6:8])

    finish_date = str(tags[-1]).split('_')[1]
    finish_time = '{}-{}-{}T00:00:00'.format(finish_date[0:4],finish_date[4:6],finish_date[6:8])

    index = -2
    while start_time == finish_time:
        start_date = str(tags[index]).split('_')[1]
        start_time = '{}-{}-{}T00:00:00'.format(start_date[0:4],
                                                start_date[4:6],
                                                start_date[6:8])
        index -= 1


    replacements['start_time'] = start_time
    replacements['finish_time'] = finish_time

    template = root_dir + '/notebooks/MARS-EXPRESS.ipynb'

    #
    # Notebook for Jenkins and HTML publication
    #
    output = 'MARS-EXPRESS_' + replacements['skd_version'] + '.ipynb'
    replacements['skd_path'] = config['skd_path']
    utils.fill_template(template, output, replacements)
    shutil.move(output, os.path.join(config['notebooks_path'],output))

    #
    # Notebook for the GitHub Laboratory
    #
    output = 'index.ipynb'
    replacements['metakernel'] = config['github_skd_path'] + '/mk/' + config['mk']
    replacements['skd_path'] = config['github_skd_path']
    utils.fill_template(template, output, replacements)
    shutil.move(output, os.path.join(config['notebooks_path'],output))

    #
    # Update the HTMLs
    #
    update_html(config)

    return


#def orbnum_check(config):
#
#
#    kernel_path = os.path.join(path, kernel_type)
#
#    #
#    # Get the kernels of type ``type`` from the ``path``/``type`` directory.
#    #
#    kernels_with_path = glob.glob(kernel_path + '/' + pattern)
#
#
#    with open(config['skd_path']+'/orbnum' 'r') as f:
#        for line in f:
#            if 'SKD_VERSION' in line:
#                replacements['skd_version'] = line.split("'")[1]
#                break
#            else:
#                replacements['skd_version'] = 'N/A'
#
#    assert True == True
#
#    return


def skd_check():

    cwd = os.getcwd()
    mks_in_dir = glob.glob('*.tm')
    mks_in_dir += glob.glob('*.TM')

    for mk_in_dir in mks_in_dir:
        output = spiops.utils.brief(os.path.join(cwd,mk_in_dir))
        print(output)
        if 'SPICE(' in output:
            raise ValueError('BRIEF utility could not run')

        now = datetime.datetime.now()
        output = spiops.utils.optiks(os.path.join(cwd, mk_in_dir),
                                     now.strftime("%Y-%m-%dT%H:%M:%S"))
        print(output)
        #if 'Unable to compute boresight.' in output:
        #     raise ValueError('BRIEF utility could not run')


    return

def update_html(config):

    cwd = os.getcwd()
    os.chdir(config['index_path'])
    em16_in_dir = list(reversed(glob.glob('ExoMars2016_*.html')))
    bc_in_dir = list(reversed(glob.glob('BEPICOLOMBO_*.html')))
    mex_in_dir = list(reversed( glob.glob('MARS-EXPRESS_*.html')))
    root_dir = os.path.dirname(__file__)

    source = os.listdir(root_dir+'/images/')
    for files in source:
        shutil.copy(root_dir+'/images/'+files, config['index_path'])


    shutil.copy(root_dir+'/templates/index.html',config['index_path'])

    with open('index_former.html', 'w+') as f:
        with open(root_dir+'/templates/index_former.html', 'r') as template:
            for line in template:
                if '{ExoMars2016}' in line:
                    if em16_in_dir:
                        for html in em16_in_dir:
                            f.write('<p><a href="http://spice.esac.esa.int/status/{}">{}</a></p>'.format(html,html.split('.')[0]))
                elif '{BepiColombo}' in line:
                    if bc_in_dir:
                        for html in bc_in_dir:
                            f.write('<p><a href="http://spice.esac.esa.int/status/{}">{}</a></p>'.format(html,html.split('.')[0]))
                elif '{Mars-Express}' in line:
                    if mex_in_dir:
                        for html in mex_in_dir:
                            f.write('<p><a href="http://spice.esac.esa.int/status/{}">{}</a></p>'.format(html,html.split('.')[0]))
                else:
                    f.write(line)
    os.chdir(cwd)


    return