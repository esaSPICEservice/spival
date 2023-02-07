#!/usr/bin/env python3

import glob
import math
import os
import datetime
import shutil
import traceback

import git

from spiops import spiops
from spiops.utils.utils import get_latest_kernel
from spival.core.skd_validator import validate_files
from spival.utils.skd_val_logger import write_final_report
from spival.utils.utils import fill_template


def write_ExoMars2016(config):

    repo = git.Repo(config['skd_path'][:-7])
    tags = repo.tags

    #
    # Set the replacements for the Notebook template
    #
    replacements = {'metakernel': config['skd_path'] + '/mk/' + config['mk']}

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
    replacements['predicted_ck'] = get_latest_kernel('ck', config['skd_path'], 'em16_tgo_sc_fsp_*_s????????_v??.bc')
    replacements['measured_ck'] = get_latest_kernel('ck', config['skd_path'], 'em16_tgo_sc_ssm_*_s????????_v??.bc')

    #
    # We obtain today's date
    #
    now = datetime.datetime.now()
    replacements['current_time'] = now.strftime("%Y-%m-%dT%H:%M:%S")

    try:
        boundary = spiops.cov_ck_ker(config['skd_path'] + '/ck/' +
                                      replacements['measured_ck'], 'TGO_SPACECRAFT', time_format='UTC')
        mes_finish_time = boundary[-1][:-4]
    except:
        print(f"WARNING: Finish time for {replacements['measured_ck']} could not be determined")
        mes_finish_time = now.strftime("%Y-%m-%dT%H:%M:%S")

    mes_start_date = datetime.datetime.strptime(mes_finish_time, '%Y-%m-%dT%H:%M:%S')
    mes_start_date = mes_start_date - datetime.timedelta(days=7)
    mes_start_time = mes_start_date.strftime("%Y-%m-%dT%H:%M:%S")

    #
    # We obtain the dates from the Tags
    #
    start_date = str(tags[-2]).split('_')[1]
    start_time = '{}-{}-{}T00:00:00'.format(start_date[0:4], start_date[4:6], start_date[6:8])

    finish_time = '{}-{}-{}T00:00:00'.format(start_date[0:4], start_date[4:6], start_date[6:8])

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

    template = config['root_dir'] + '/notebooks/ExoMars2016.ipynb'

    #
    # Notebook for Jenkins and HTML publication
    #
    output = 'ExoMars2016_' + replacements['skd_version'] + '.ipynb'
    replacements['skd_path'] = config['skd_path']
    fill_template(template, output, replacements)
    shutil.move(output, os.path.join(config['notebooks_path'], output))

    #
    # Notebook for the GitHub Laboratory
    #
    output = 'index.ipynb'
    replacements['metakernel'] = config['github_skd_path'] + '/mk/' + config['mk']
    replacements['skd_path'] = config['github_skd_path']
    fill_template(template, output, replacements)
    shutil.move(output, os.path.join(config['notebooks_path'], output))

    #
    # Update the HTMLs
    #
    update_html(config)

    return


def write_BepiColombo(config):

    repo = git.Repo(config['skd_path'][:-7])
    tags = repo.tags

    #
    # Set the replacements for the Notebook template
    #
    replacements = {'metakernel': config['skd_path'] + '/mk/' + config['mk']}

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
    replacements['predicted_ck'] = get_latest_kernel('ck', config['skd_path'], 'bc_mpo_sc_fcp_00*.bc')
    replacements['measured_ck'] = get_latest_kernel('ck', config['skd_path'], 'bc_mpo_sc_scm_*_s????????_v??.bc')
    replacements['reconstructed_spk'] = get_latest_kernel('spk', config['skd_path'], 'bc_mpo_fcp_0*_v??.bsp')

    #
    # We obtain today's date
    #
    now = datetime.datetime.now()
    replacements['current_time'] = now.strftime("%Y-%m-%dT%H:%M:%S")

    boundary = spiops.cov_ck_ker(config['skd_path'] + '/ck/' +
                                  replacements['measured_ck'], 'MPO_SPACECRAFT', time_format='UTC')

    mes_finish_time = boundary[-1][:-4]
    mes_start_date = datetime.datetime.strptime(mes_finish_time, '%Y-%m-%dT%H:%M:%S')
    mes_start_date = mes_start_date - datetime.timedelta(days=7)
    mes_start_time = mes_start_date.strftime("%Y-%m-%dT%H:%M:%S")

    #
    # We obtain the dates from the Tags
    #
    start_date = str(tags[-2]).split('_')[1]
    start_time = '{}-{}-{}T00:00:00'.format(start_date[0:4], start_date[4:6], start_date[6:8])

    finish_time = '{}-{}-{}T00:00:00'.format(start_date[0:4], start_date[4:6], start_date[6:8])

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

    template = config['root_dir'] + '/notebooks/BEPICOLOMBO.ipynb'

    #
    # Notebook for Jenkins and HTML publication
    #
    output = 'BEPICOLOMBO_' + replacements['skd_version'] + '.ipynb'
    replacements['skd_path'] = config['skd_path']
    fill_template(template, output, replacements)
    shutil.move(output, os.path.join(config['notebooks_path'], output))

    #
    # Notebook for the GitHub Laboratory
    #
    output = 'index.ipynb'
    replacements['metakernel'] = config['github_skd_path'] + '/mk/' + config['mk']
    replacements['skd_path'] = config['github_skd_path']
    fill_template(template, output, replacements)
    shutil.move(output, os.path.join(config['notebooks_path'], output))

    #
    # Update the HTMLs
    #
    update_html(config)

    return


def write_JUICE(config):

    #
    # Set the replacements for the Notebook template
    #
    replacements = {'metakernel': config['skd_path'] + '/mk/' + config['mk']}

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
    replacements['predicted_ck'] = get_latest_kernel('ck', config['skd_path'], config['predicted_ck'])
    # replacements['measured_ck'] = get_latest_kernel('ck', config['skd_path'],'bc_mpo_sc_scm_*_s????????_v??.bc')
    replacements['reconstructed_spk'] = get_latest_kernel('spk', config['skd_path'], config['reconstructed_spk'])

    #
    # We obtain today's date
    #
    now = datetime.datetime.now()
    replacements['current_time'] = now.strftime("%Y-%m-%dT%H:%M:%S")

    boundary = spiops.cov_ck_ker(config['skd_path'] + '/ck/' +
                                 replacements['predicted_ck'], 'JUICE_SPACECRAFT_PLAN', time_format='UTC')

    mes_finish_time = boundary[-1][:-4]

    if "check_full_coverage" in config and config["check_full_coverage"] is True:
        # Check the full predicted_ck coverage
        mes_start_time = boundary[0][:-4]
        replacements['XM-C1_description'] = "The metakernel is loaded, the scenario covers the full coverage of the latest Predicted Attitude Kernel."

        if "coverage_margin" in config:
            mes_start_time = datetime.datetime.strptime(mes_start_time, '%Y-%m-%dT%H:%M:%S')
            mes_start_time = mes_start_time + datetime.timedelta(seconds=config["coverage_margin"])
            mes_start_time = mes_start_time.strftime("%Y-%m-%dT%H:%M:%S")

            mes_finish_time = datetime.datetime.strptime(mes_finish_time, '%Y-%m-%dT%H:%M:%S')
            mes_finish_time = mes_finish_time - datetime.timedelta(seconds=config["coverage_margin"])
            mes_finish_time = mes_finish_time.strftime("%Y-%m-%dT%H:%M:%S")

            replacements['XM-C1_description'] = "The metakernel is loaded, the scenario covers the full coverage of the latest Predicted Attitude Kernel with a margin of " + str(config["coverage_margin"]) + " seconds."

    else:
        # Check only last week
        mes_start_date = datetime.datetime.strptime(mes_finish_time, '%Y-%m-%dT%H:%M:%S')
        mes_start_date = mes_start_date - datetime.timedelta(days=7)
        mes_start_time = mes_start_date.strftime("%Y-%m-%dT%H:%M:%S")

        replacements['XM-C1_description'] = "The metakernel is loaded, the scenario covers a week with a finish time set by the end of coverage of the latest Predicted Attitude Kernel."

    replacements['start_time_measured'] = mes_start_time
    replacements['finish_time_measured'] = mes_finish_time

    if "samples" in config:
        start_date = datetime.datetime.strptime(mes_start_time, '%Y-%m-%dT%H:%M:%S')
        end_date = datetime.datetime.strptime(mes_finish_time, '%Y-%m-%dT%H:%M:%S')
        replacements['resolution'] = str(math.ceil((end_date - start_date).total_seconds() / config['samples']))
    else:
        replacements['resolution'] = "60"

    template = config['root_dir'] + '/notebooks/JUICE.ipynb'

    #
    # Notebook for Jenkins and HTML publication
    #
    output = 'JUICE_' + replacements['skd_version'] + '.ipynb'
    replacements['skd_path'] = config['skd_path']
    fill_template(template, output, replacements)
    shutil.move(output, os.path.join(config['notebooks_path'], output))

    #
    # Notebook for the GitHub Laboratory
    #
    output = 'index.ipynb'
    replacements['metakernel'] = config['github_skd_path'] + '/mk/' + config['mk']
    replacements['skd_path'] = config['github_skd_path']
    fill_template(template, output, replacements)
    shutil.move(output, os.path.join(config['notebooks_path'], output))

    #
    # Update the HTMLs
    #
    update_html(config)

    return


def write_MarsExpress(config):

    repo = git.Repo(config['skd_path'][:-7])
    tags = repo.tags

    #
    # Set the replacements for the Notebook template
    #
    replacements = {'metakernel': config['skd_path'] + '/mk/' + config['mk']}

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
    start_time = '{}-{}-{}T00:00:00'.format(start_date[0:4], start_date[4:6], start_date[6:8])

    finish_date = str(tags[-1]).split('_')[1]
    finish_time = '{}-{}-{}T00:00:00'.format(finish_date[0:4], finish_date[4:6], finish_date[6:8])

    index = -2
    while start_time == finish_time:
        start_date = str(tags[index]).split('_')[1]
        start_time = '{}-{}-{}T00:00:00'.format(start_date[0:4],
                                                start_date[4:6],
                                                start_date[6:8])
        index -= 1

    print('Notebook start time {}'.format(start_time))
    print('Notebook finish time {}'.format(finish_time))

    replacements['start_time'] = start_time
    replacements['finish_time'] = finish_time

    template = config['root_dir'] + '/notebooks/MARS-EXPRESS.ipynb'

    #
    # Notebook for Jenkins and HTML publication
    #
    output = 'MARS-EXPRESS_' + replacements['skd_version'] + '.ipynb'
    replacements['skd_path'] = config['skd_path']
    fill_template(template, output, replacements)
    shutil.move(output, os.path.join(config['notebooks_path'], output))

    #
    # Notebook for the GitHub Laboratory
    #
    output = 'index.ipynb'
    replacements['metakernel'] = config['github_skd_path'] + '/mk/' + config['mk']
    replacements['skd_path'] = config['github_skd_path']
    fill_template(template, output, replacements)
    shutil.move(output, os.path.join(config['notebooks_path'], output))

    #
    # Update the HTMLs
    #
    update_html(config)

    return


#  def orbnum_check(config):
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


def check(dir_path=False):

    if dir_path:
        cwd = dir_path
        os.chdir(dir_path)
    else:
        cwd = os.getcwd()

    mks_in_dir = glob.glob('*.tm')
    mks_in_dir += glob.glob('*.TM')

    for mk_in_dir in mks_in_dir:
        output = spiops.brief(os.path.join(cwd, mk_in_dir))
        print(output)
        if 'SPICE(' in output:
            raise ValueError('BRIEF utility could not run')

        now = datetime.datetime.now()
        output = spiops.optiks(os.path.join(cwd, mk_in_dir), now.strftime("%Y-%m-%dT%H:%M:%S"))
        print(output)
        #  if 'Unable to compute boresight.' in output:
        #     raise ValueError('BRIEF utility could not run')

    os.chdir(cwd)

    return


def validate(path_arr=None):
    try:
        files = []
        if path_arr is None:
            path_arr = []

        for path in path_arr:

            if "*" in path or "?" in path:
                if os.path.sep not in path:
                    path = "**/" + path
                files.extend(list(glob.iglob(path, recursive=True)))
                continue

            if not os.path.exists(path):
                raise Exception("Path doesn't exists: " + str(path))

            if os.path.isfile(path):
                files.append(path)

            elif os.path.isdir(path):
                files.extend(list(glob.iglob(path + '/**/*', recursive=True)))

        if not(len(files)):
            print("Not any file found matching: " + str(path_arr))
            return 0

        all_files_are_valid = validate_files(files)

        write_final_report(path_arr, len(files))

        if all_files_are_valid:
            print("")
            print("=============================================================")
            print("==========           KERNEL FILES VALID!!!!         =========")
            print("=============================================================")
            print("")
            return 0

        else:
            print("")
            print("=============================================================")
            print("==========          NOT VALID KERNEL FILES          =========")
            print("=============================================================")
            print("")
            return 1

    except Exception as ex:
        print("")
        print("=============================================================")
        print("==========              ERROR IN VALIDATION         =========")
        print("=============================================================")
        print("")
        print(" Exception: " + str(ex))
        print("")
        traceback.print_exc()
        print("")

        return 1


def update_html(config):

    cwd = os.getcwd()
    os.chdir(config['index_path'])
    em16_in_dir = list(reversed(glob.glob('ExoMars2016_*.html')))
    bc_in_dir = list(reversed(glob.glob('BEPICOLOMBO_*.html')))
    juice_in_dir = list(reversed(glob.glob('JUICE_*.html')))
    mex_in_dir = list(reversed(glob.glob('MARS-EXPRESS_*.html')))
    adcsng_in_dir = list(reversed(glob.glob('adcsng_v*.html')))
    root_dir = config['root_dir']

    source = os.listdir(root_dir+'/images/')
    for files in source:
        shutil.copy(root_dir+'/images/' + files, config['index_path'])

    shutil.copy(root_dir+'/templates/index.html', config['index_path'])
    shutil.copy(root_dir+'/templates/spival.html', config['index_path'])

    with open('index_former.html', 'w+') as f:
        with open(root_dir+'/templates/index_former.html', 'r') as template:
            for line in template:
                if '{ExoMars2016}' in line:
                    if em16_in_dir:
                        for html in em16_in_dir:
                            f.write('<p><a href="http://spice.esac.esa.int/status/{}">{}</a></p>'
                                    .format(html, html.split('.')[0]))
                elif '{BepiColombo}' in line:
                    if bc_in_dir:
                        for html in bc_in_dir:
                            f.write('<p><a href="http://spice.esac.esa.int/status/{}">{}</a></p>'
                                    .format(html, html.split('.')[0]))
                elif '{JUICE}' in line:
                    if juice_in_dir:
                        for html in juice_in_dir:
                            f.write('<p><a href="http://spice.esac.esa.int/status/{}">{}</a></p>'
                                    .format(html, html.split('.')[0]))
                elif '{Mars-Express}' in line:
                    if mex_in_dir:
                        for html in mex_in_dir:
                            f.write('<p><a href="http://spice.esac.esa.int/status/{}">{}</a></p>'
                                    .format(html, html.split('.')[0]))
                else:
                    f.write(line)

    with open('index_adcsng_former.html', 'w+') as f:
        with open(root_dir + '/templates/index_adcsng_former.html', 'r') as template:
            for line in template:
                if '{adcsng}' in line:
                    if adcsng_in_dir:
                        for html in adcsng_in_dir:
                            f.write(
                                '<p><a href="http://spice.esac.esa.int/status/{}">{}</a></p>'.format(
                                    html, html))
                else:
                    f.write(line)

    os.chdir(cwd)

    return

