#!/usr/bin/env python3

import glob
import os
import datetime
import shutil

import spiops

from .utils import utils

def write_ExoMars2016(config):

    root_dir = os.path.dirname(__file__)

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
    replacements['predicted_ck'] = spiops.utils.get_latest_kernel('ck',config['skd_path'],'em16_tgo_sc_fsp_*_s????????_v*.bc')
    replacements['measured_ck'] = spiops.utils.get_latest_kernel('ck', config['skd_path'],'em16_tgo_sc_ssm_*_s????????_v??.bc')

        #
        # We obtain today's date
        #
    now = datetime.datetime.now()
    replacements['current_time'] = now.strftime("%Y-%M-%dT%H:%M")

    boundary  = spiops.cov_ck_ker(config['skd_path']+ '/ck/' + replacements['measured_ck'], 'TGO_SPACECRAFT', time_format='UTC')

    replacements['start_time'] = boundary[0]
    replacements['finish_time'] = boundary[-1]

    template = root_dir + '/notebooks/ExoMars2016.py'

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

        output = spiops.utils.optiks(os.path.join(cwd, mk_in_dir),
                                     '2019-01-01T00:00:00')
        print(output)
        #if 'Unable to compute boresight.' in output:
        #     raise ValueError('BRIEF utility could not run')


    return