import hashlib
import os
import errno
import select
import shutil
import fileinput
import glob
import re
import logging
import json
import subprocess
from datetime import datetime

from os import listdir
from os.path import isfile, join
from shutil import move, copyfile
from tempfile import mkstemp

MAX_LINE_LENGTH = 80
BAD_CHAR_KEYWORDS = ["<<<<<<< ", ">>>>>>> "]


def mk2list(mk):
    inside_data_section = False
    path_symbol = ''
    for_next_line = ''
    ker_mk_list = []
    with open(mk, 'r') as f:
        for line in f:

            if inside_data_section:

                if not path_symbol:
                    if 'PATH_SYMBOLS' in line.upper():
                        path_symbol = '$' + line.split("'")[1]
                else:

                    if '\\begintext' in line:
                        break

                    if for_next_line:
                        line = for_next_line + line.strip()
                        kernel = line.split(path_symbol)[1].replace("'", "")
                        ker_mk_list.append(kernel)
                        for_next_line = ''
                    else:
                        if path_symbol in line:
                            line = line.strip()

                            if line.endswith("+'"):
                                for_next_line = line[0:-2]
                            else:
                                kernel = line.split(path_symbol)[1].replace("'", "")
                                ker_mk_list.append(kernel)

            elif '\\begindata' in line:
                inside_data_section = True

    return ker_mk_list


def replace(file_path, pattern, subst):
    replaced = False

    # Create temp file
    fh, abs_path = mkstemp()
    with os.fdopen(fh, 'w') as new_file:
        with open(file_path) as old_file:
            for line in old_file:

                updated_line = line.replace(pattern, subst)
                if '$KERNELS/' in line and len(updated_line.strip()) > 82:
                    updated_line = os.sep.join(updated_line.split(os.sep)[0:-1]) + \
                                   os.sep + "+'\n" + 27 * " " + "'" + \
                                   updated_line.split(os.sep)[-1]

                new_file.write(updated_line)

                # flag for replacing having happened
                if updated_line != line:
                    replaced = True

    # Remove original file
    if replaced:
        os.remove(file_path)

        # Update the permissions
        os.chmod(abs_path, 0o644)

        # Move new file
        move(abs_path, file_path)

        return True

    return False


def format_str(string, dictionary):
    """
    Return a character string in which all the {KEYWORD} tokens existing in
    the input ``string`` have been replaced by the corresponding value
    contained in the input ``dictionary`` should these KEYWORD=value pairs
    exist in the ``dictionary`` and remain untouched otherwise.

    :param string: str
       Character string containing {KEYWORD} tokens to be replaced by the
       corresponding values provided in the ``dictionary``.
    :param dictionary: dict
       Dictionary that provides several or all the values for the {KEYWORD}s
       contained in the input character ``string``
    :return: str
       Character string in which all the {KEYWORD} tokens in the input
       ``string`` for which a value exists in the input ``dictionary`` have
       been replaced by that value.
    """
    tokens = string.split('}')
    output = []
    for token in tokens[:-1]:
        if token.split('{')[-1] in dictionary.keys():
            output.append((token + '}').format(**dictionary))
        else:
            output.append(token + '}')

    return ''.join(output) + tokens[-1]


def fill_template(template,
                  file,
                  replacements,
                  cleanup=False):
    #
    # If the temp   late file is equal to the output file then we need to create a temporary template - which will be
    # a duplicate - in order to write in the file. A situation where we would like to have them be the same is
    # for example if we call this function several times in a row, replacing keywords in the template in steps
    #
    if template == file:
        with open(file, 'r') as f:
            with open('fill_template.temp', "w+") as t:
                for line in f:
                    t.write(line)

        template = 'fill_template.temp'

    with open(file, "w+") as f:
        #
        # Items are replaced as per correspondence in between the replacements dictionary
        #
        with open(template, 'r') as t:
            for line in t:
                if '{' in line:
                    for k, v in replacements.items():
                        if '{' + k + '}' in line:
                            line = line.replace('{' + k + '}', v)
                #
                # We need to manage the lenght of the line and slpit it if need be.
                #
                # if 'LSK_FILE_NAME' in line or 'FK_FILE_NAME' in line or 'SCLK_FILE_NAME' in line:
                #    if len(line.split("'")[1]) > 80:
                #        line = "'\n      SCLK_FILE_NAME         += '/".join(line.rsplit('/',1))

                f.write(line)

                #
                # If the option cleanup is set as true, we remove the keyword assignments in the filled templated which
                # are unfilled (they should be optional)
                #

    if cleanup:

        with open(file, 'r') as f:
            with open('fill_template.temp', 'w+') as t:
                for line in f:
                    t.write(line)

        with open(file, 'w+') as f:
            with open('fill_template.temp', 'r') as t:
                for line in t:
                    if '{' not in line:
                        f.write(line)

    # The temporary files are removed
    if os.path.isfile('fill_template.temp'):
        os.remove('fill_template.temp')


def get_latest_kernel(kernel_type, path, pattern, dates=False,
                      excluded_kernels=False,
                      mkgen=False):
    """
    Returns the name of the latest MK, LSK, FK or SCLK present in the path

    :param kernel_type: Kernel type (lsk, sclk, fk) which also defines the subdirectory name.
    :type kernel_type: str
    :param path: Path to the root of the SPICE directory where the kernels are store in a directory named ``type``.
    :type path: str
    :param patterns: Patterns to search for that defines the kernel ``type`` file naming scheme.
    :type patterns: list
    :return: Name of the latest kernel of ``type`` that matches the naming scheme defined in ``token`` present in the ``path`` directory.
    :rtype: strÐ
    :raises:
       KernelNotFound if no kernel of ``type`` matching the naming scheme
       defined in ``token is present in the ``path`` directory
    """
    kernels = []
    kernel_path = os.path.join(path, kernel_type)

    #
    # Get the kernels of type ``type`` from the ``path``/``type`` directory.
    #
    kernels_with_path = glob.glob(kernel_path + '/' + pattern)

    #
    # Include kernels in former_versions if the directory exists except for
    # meta-kernel generation
    #
    if os.path.isdir(kernel_path + '/former_versions') and not mkgen:
        kernels_with_path += glob.glob(kernel_path + '/former_versions/' + pattern )

    for kernel in kernels_with_path:
        kernels.append(kernel.split('/')[-1])

    #
    # Put the kernels in order
    #
    kernels.sort()

    #
    # We remove the kernel if it is included in the excluded kernels list
    #
    if excluded_kernels:
        for excluded_kernel in excluded_kernels:
            for kernel in kernels:
                if excluded_kernel.split('*')[0] in kernel:
                    kernels.remove(kernel)

    if not dates:
        #
        # Return the latest kernel
        #
        try:
            return kernels.pop()
        except:
            logging.warning('No kernels found with pattern {}'.format(pattern))
            return []
    else:
        #
        # Return all the kernels with a given date
        #
        previous_kernel = ''
        kernels_date = []
        for kernel in kernels:
            if previous_kernel \
                    and re.split('_V\d\d', previous_kernel.upper())[0] == re.split('_V\d\d', kernel.upper())[0]\
                    or re.split('_V\d\d\d', previous_kernel.upper())[0] == re.split('_V\d\d\d', kernel.upper())[0]:
                kernels_date.remove(previous_kernel)

            previous_kernel = kernel
            kernels_date.append(kernel)

        return kernels_date


def get_increment_kernels(mission, files_list):
    #
    # copy missing files from previous increment
    #
    if mission.pds == '3' and mission.increment:
        logging.info("Copying missing files from previous increment...")
        incr_dir = mission.increment + '/DATA/'
        incr_kernel_directory_list = listdir(incr_dir)
        for directory in incr_kernel_directory_list:
            dir = incr_dir + directory
            incr_files = [join(dir, f) for f in listdir(dir) if isfile(join(dir, f))]
            for incr_file in incr_files:
                incr_file = incr_file.split('/')[-1]
                if not incr_file in files_list:
                    src = incr_dir + directory + '/' + incr_file
                    dst_dir = mission.bundle_directory + '/DATA/' + directory
                    if not os.path.isdir(dst_dir):
                        os.mkdir(dst_dir)
                    dst = dst_dir + '/' + incr_file
                    if not incr_file.lower().endswith(".lbl"):
                        logging.info("      Copying: " + directory + '/' + incr_file)
                    copyfile(src, dst)

        # Copy ORBNUM files if any
        orbdir = mission.bundle_directory + '/EXTRAS/ORBNUM/'
        incr_orbdir = mission.increment + '/EXTRAS/ORBNUM/'
        if os.path.isdir(incr_orbdir):
            files = [join(orbdir, f) for f in listdir(orbdir) if isfile(join(orbdir, f))]
            incr_files = [join(incr_orbdir, f) for f in listdir(incr_orbdir) if isfile(join(incr_orbdir, f))]
            for incr_file in incr_files:
                if incr_file not in files:
                    src = incr_orbdir + incr_file.split('/')[-1]
                    dst = orbdir + incr_file.split('/')[-1]
                    if not os.path.isdir(orbdir):
                        os.mkdir(orbdir)
                    logging.info("Copying: " + src)
                    copyfile(src, dst)
    return


def extension2type(kernel):

    kernel_type_map = {
        "TI":  "IK",
        "TF":  "FK",
        "TM":  "MK",
        "TSC": "SCLK",
        "TLS": "LSK",
        "TPC": "PCK",
        "BC":  "CK",
        "BSP": "SPK",
        "BPC": "PCK",
        "BES": "EK",
        "BDS": "DSK",
        "ORB": "ORB"
    }

    try:
        #
        # Kernel is an object
        #
        kernel_type = kernel_type_map[kernel.extension.upper()].lower()
    except:
        #
        # Kernel is a string
        #
        kernel_type = kernel_type_map[kernel.split('.')[-1].upper()].lower()

    return kernel_type


def type2extension(kernel_type):

    kernel_type = kernel_type.upper()


    kernel_type_map = {
        "IK": ["ti"],
        "FK": ["tf"],
        "MK": ["tm"],
        "SCLK": ["tsc"],
        "LSK": ["tls"],
        "PCK": ["tpc","bpc"],
        "CK": ["bc"],
        "SPK": ["bsp"],
        "DSK": ["bds"]
    }

    kernel_extension = kernel_type_map[kernel_type]

    return kernel_extension


def extension2PDS3type(kernel):

    kernel_type_map = {
        "TI":  "INSTRUMENT",
        "TF":  "FRAMES",
        "TSC": "CLOCK_COEFFICIENTS",
        "TLS": "LEAPSECONDS",
        "TPC": "TARGET_CONSTANTS",
        "BC":  "POINTING",
        "BSP": "EPHEMERIS",
        "BPC": "TARGET_CONSTANTS",
        "BDS": "SHAPE",
        "BES": "EVENTS",
        "ORB": "ORBNUM",
        "TM": "METAKERNEL"
    }

    kernel_type = kernel_type_map[kernel.extension.upper()].upper()

    return kernel_type


def mk2list(mk):

    path_symbol = ''
    ker_mk_list = []
    with open(mk, 'r') as f:
        for line in f:

            if path_symbol:
                if path_symbol in line:

                    kernel = line.split(path_symbol)[1]
                    kernel = kernel.strip()
                    kernel = kernel[:-1]
                    kernel = kernel.split('/')[-1]

                    ker_mk_list.append(kernel)

            if 'PATH_SYMBOLS' in line.upper():
                path_symbol = '$' + line.split("'")[1]

    return ker_mk_list


def add_carriage_return(line):
    #
    # Adding CR to line
    #
    if '\r\n' not in line:
        line = line.replace('\n', '\r\n')
    if '\r\n' not in line:
        line += '\r\n'

    return line


def get_skd_spacecrafts(mission):

    sc = ['{}'.format(mission.spacecraft)]

    sec_scs = mission.secondary_spacecrafts.split(',')
    if not isinstance(sec_scs, list):
        sec_scs = [sec_scs]

    scs = sc + sec_scs

    sc_list_for_label = ''

    context_products = mission.context_products

    for sc in scs:
        if sc:
            sc_name = sc.split(',')[0].strip()
            for product in context_products:
                if product['name'][0].upper() == sc_name.upper():
                    sc_lid = product['lidvid'].split('::')[0]

            sc_list_for_label += \
            '            <Observing_System_Component>\r\n' + \
           f'                <name>{sc_name}</name>\r\n' + \
            '                <type>Spacecraft</type>\r\n' + \
            '                <Internal_Reference>\r\n' + \
           f'                    <lid_reference>{sc_lid}</lid_reference>\r\n' + \
            '                    <reference_type>is_instrument_host</reference_type>\r\n' + \
            '                </Internal_Reference>\r\n' + \
            '            </Observing_System_Component>\r\n'

    sc_list_for_label = sc_list_for_label.rstrip() + '\r\n'

    return sc_list_for_label


def get_skd_targets(mission, target_reference_type):

    tar = [mission.target]

    sec_tar = mission.secondary_targets.split(',')
    if not isinstance(sec_tar, list):
        sec_tar = [sec_tar]

    tars = tar + sec_tar

    tar_list_for_label = ''

    context_products = mission.context_products

    for tar in tars:
        if tar:

            target_name = tar
            for product in context_products:
                if product['name'][0].upper() == target_name.upper():
                    target_lid = product['lidvid'].split('::')[0]
                    target_type = product['type'][0].capitalize()

            tar_list_for_label += \
            '        <Target_Identification>\r\n' + \
           f'            <name>{target_name}</name>\r\n' + \
           f'            <type>{target_type}</type>\r\n' + \
            '            <Internal_Reference>\r\n' + \
           f'                <lid_reference>{target_lid}</lid_reference>\r\n' + \
           f'                <reference_type>{target_reference_type}</reference_type>\r\n' + \
            '            </Internal_Reference>\r\n' + \
            '        </Target_Identification>\r\n'

    tar_list_for_label = tar_list_for_label.rstrip() + '\r\n'

    return tar_list_for_label


def get_context_products(mission):

    registered_context_products_file = f'{mission.root_dir}/config/registered_context_products.json'
    with open(registered_context_products_file, 'r') as f:
              context_products = json.load(f)['Product_Context']

    local_context_products_file = f'{mission.root_dir}/config/{mission.accronym}_context_products.json'
    with open(local_context_products_file, 'r') as f:
              context_products += json.load(f)['Product_Context']

    return context_products


def get_spacecraft_text(mission):

    # Define PDS4_SPACECRAFT_TEXT
    # Usually this text shall be:
    # "Contains the SPICE System kernel files for the TGO spacecraft, its instruments and targets."
    # But for missions with many spacecrafts shall be:
    # "Contains the SPICE System kernel files for the MPO, MMO and MTM spacecrafts, their instruments and targets."
    # Note that templates are defined as: "files for the $PDS4_SPACECRAFT_TEXT instruments and targets."

    spacecraft_text = mission.spacecraft

    if len(mission.secondary_spacecrafts):
        sec_scs = mission.secondary_spacecrafts.split(",")
        for i in range(len(sec_scs)):
            spacecraft_text += (", " if (i < len(sec_scs) - 1) else " and ") + sec_scs[i].strip()
        spacecraft_text += " spacecrafts, their"
    else:
        spacecraft_text += " spacecraft and its"

    return spacecraft_text


def is_empty_file(file):
    return os.stat(file).st_size == 0


def has_badchars(file_path):
    file = open(file_path, 'r')
    linen = 0
    badchars_detected = False
    for line in file.readlines():
        linen += 1
        for i in range(0, len(line), 1):
            e = line[i]
            if (re.sub('[ -~]', '', e)) != "" and e != '\n':
                print('ERROR!! - NON ASCII CHAR: \'' + e + '\' detected in file: ' + file_path + " at line: " + str(linen))
                badchars_detected = True

        for bad_char_keyword in BAD_CHAR_KEYWORDS:
            if bad_char_keyword in line:
                print('ERROR!! - BAD_CHAR_KEYWORD found: \'' + bad_char_keyword + '\' detected in file: ' + file_path + " at line: " + str(linen))
                badchars_detected = True

    file.close()
    return badchars_detected


def exceeds_line_lengths(file, max_length=MAX_LINE_LENGTH, ignore_lines=[]):
    f = open(file).readlines()
    linen = 0
    has_long_lines = False
    for i in range(0, len(f), 1):
        linen += 1
        if len(f[i].replace('\n', '')) > max_length:
            line_ignored = False

            for ignore_line in ignore_lines:
                if ignore_line in f[i]:
                    line_ignored = True
                    break

            if not line_ignored:
                print('ERROR!! - EXCEEDS LINE LENGTH: Line nr: ' + str(linen) + ' in file ' + file)
                print(f[i])
                has_long_lines = True

    return has_long_lines


def validate_indentation(file, indentation=3):
    f = open(file).readlines()
    linen = 0
    has_wrong_indentation = False
    for i in range(0, len(f), 1):
        linen += 1
        line = f[i].replace('\n', '')
        spaces = len(line) - len(line.lstrip())
        if spaces and spaces % indentation != 0:
            print('WARNING!! - WRONG INDENTATION: Line nr: ' + str(linen) + ' in file ' + file)
            print("'" + line + "'")
            has_wrong_indentation = True

    return has_wrong_indentation


def validate_trailing_chars(file):
    f = open(file).readlines()
    linen = 0
    has_trailing_chars = False
    for i in range(0, len(f), 1):
        linen += 1
        line = f[i].replace('\n', '')
        trailing_chars = len(line) - len(line.rstrip())
        if trailing_chars > 0:
            print('WARNING!! - Found ' + str(trailing_chars) + ' trailing char at Line nr: ' + str(linen) + ' in file ' + file)
            print("'" + line + "'")
            has_trailing_chars = True

    return has_trailing_chars


def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def copy(src, dest):
    try:
        shutil.copytree(src, dest)
    except OSError as e:
        # If the error was caused because the source wasn't a directory
        if e.errno == errno.ENOTDIR:
            shutil.copy(src, dest)
        else:
            logging.warning('Directory not copied, probably because the increment '
                            'directory exists.\n Error: %s' % e)


# Given a filename with a given format, returns a datetime with the date expressed in the filename
# Eg: filename => MEX_SC_201022_SADE_M.TAB ,  date_format => 7|6|%y%m%d or ["7|6|%y%m%d", "7|6|yyy%m%d"]
#     Returns =>  datetime with value: 2020-10-22 00:00:00.000
# Note: Each date_format element shall have the following format=> start_index|date_length|strptime_format
#       date_format can be a string or a list of date format strings, in case of list all the formats will be
#       tried. The first valid date parsed will be returned.
def get_date_from_filename(filename, date_format):
    date_str = ""
    exception_str = ""

    # Get only the filename, avoid absolute or relative paths
    if os.sep in filename:
        filename = os.path.basename(filename)

    # If date_format is not of type list convert it to list.
    if not isinstance(date_format, list):
        date_format = [date_format]

    for date_format_elem in date_format:
        date_format_parts = date_format_elem.split("|")
        try:

            if len(date_format_parts) != 3:
                raise Exception("Wrong 'source_date_format': 'start_index|date_length|strptime_format' "
                                + "in config for file: " + filename)

            start_idx = int(date_format_parts[0])
            end_idx = start_idx + int(date_format_parts[1])
            date_str = filename[start_idx:end_idx]
            return datetime.strptime(date_str, date_format_parts[2])

        except:
            exception_str += "Wrong 'source_date_format': 'start_index|date_length|strptime_format' in config for " \
                             "file: " + filename + " , format: " + date_format_elem + " , extracted date: " + date_str \
                             + "\n"

    # In case of any date returned, raise exception with all tries done.
    raise Exception(exception_str)


def safe_make_directory(i):
    '''Makes a folder if not present'''
    try:
        os.mkdir(i)
    except:
        pass


def read_errata(file):

    errata_string = ''
    for line in fileinput.input(file):
        line = line.rstrip()
        line += '\n'
        errata_string += line

    return errata_string


def commnt_read(kernel_path, directories=None):

    exe_path = directories.executables + '/' if directories is not None else ""

    command_line_process = subprocess.Popen([exe_path + 'commnt', '-r',
                                             check_spice_path(kernel_path)],
                                             bufsize=8192, shell=False,
                                             stdout=subprocess.PIPE,
                                             stderr=subprocess.PIPE)
    process_output = ""
    dataend = False
    while (command_line_process.returncode is None) or (not dataend):
        command_line_process.poll()
        dataend = False

        ready = select.select([command_line_process.stdout, command_line_process.stderr], [], [], 1.0)

        if command_line_process.stderr in ready[0]:
            data = command_line_process.stderr.read(1024)
            if len(data) > 0:
                raise Exception(data)

        if command_line_process.stdout in ready[0]:
            data = command_line_process.stdout.read(1024)
            if len(data) == 0:  # Read of zero bytes means EOF
                dataend = True
            else:
                process_output += data.decode('utf-8')

    return process_output


def commnt_add(kernel_path, commnt_path, directories):
    command_line_process = subprocess.Popen(
        [directories.executables + '/' + 'commnt', '-a', check_spice_path(kernel_path), check_spice_path(commnt_path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT)
    command_line_process.wait()
    process_output, _ = command_line_process.communicate()
    return process_output.decode('utf-8')


def commnt_delete(kernel_path, directories):
    command_line_process = subprocess.Popen(
        [directories.executables + '/' + 'commnt', '-d', check_spice_path(kernel_path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT)
    command_line_process.wait()
    process_output, _ = command_line_process.communicate()
    return


def commnt_extract(kernel_path, commnt_path, directories):
    command_line_process = subprocess.Popen(
        [directories.executables + '/' + 'commnt', '-e', kernel_path, commnt_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT)
    command_line_process.wait()
    return


def run_ckbrief(kernel_path, support_kernels, directories):
    command_line_process = subprocess.Popen([directories.executables + '/' +
                                             'ckbrief', check_spice_path(kernel_path), support_kernels, '-utc', '-g'],
                                            stdout=subprocess.PIPE,
                                            stderr=subprocess.STDOUT)
    command_line_process.wait()
    process_output, _ = command_line_process.communicate()
    coverage_text = process_output.decode("utf-8")
    return coverage_text


def dafcat_kernels(merged_kernel, kernels):
    write_daf_file(kernels, 'grouped.daf')
    write_dafcat_comments(kernels, 'dafcat.commnt')
    log = run_dafcat(merged_kernel, "grouped.daf", kernels[0].directories)
    log += commnt_add(merged_kernel, 'dafcat.commnt', kernels[0].directories)
    return log


def run_dafcat(kernel_path, daf_file, directories):
    cmd = directories.executables + os.sep + 'dafcat < ' + daf_file + ' ' + kernel_path
    command_line_process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    command_line_process.wait()
    process_output = command_line_process.communicate()[0]
    return process_output.decode('utf-8')


def write_daf_file(kernels, daf_file):
    with open(daf_file, 'w') as i:
        for kernel in kernels:
            i.write(os.path.join(kernel.working_directory, str(kernel.name) + '\n'))


def write_dafcat_comments(kernels, comment_file):
    with open(comment_file, 'a') as c:
        for kernel in kernels:
            with open(os.path.join(kernel.working_directory, str(kernel.name).split('.')[0] + '.commnt'), 'r') as d:
                for line in d:
                    c.write(line)


def find(name, path):
    for root, dirs, files in os.walk(path):
        if name in files:
            return os.path.join(root, name)


def copy_files(filenames, source_dir, destination_dir):
    for filename in filenames:
        copyfile(os.path.join(source_dir, filename), os.path.join(destination_dir, filename))


def check_spice_path(spice_path):
    if os.path.isabs(spice_path) and \
            ((os.path.isfile(spice_path) and len(spice_path) > 100)
                    or (os.path.isdir(spice_path) and len(spice_path) > 60)):
        spice_path = os.path.relpath(spice_path, os.getcwd())

    return spice_path


def read_all_text(file_path):
    text = ""
    with open(file_path, 'r') as d:
        lines = d.readlines()
        text = "".join(lines)
    return text


def get_section_text_from_kernel_comments(kernel_path, section_name, directories=None):
    try:

        # First check if is a binary kernel or text kernel
        name, extension = os.path.splitext(kernel_path)
        if str(extension).lower().startswith(".t"):
            # Is a text kernel, just read the file:
            kernel_comments = read_all_text(kernel_path)
        else:
            # Shall be a binary kernel, use commnt read:
            kernel_comments = commnt_read(kernel_path, directories)

        kernel_comments = kernel_comments.splitlines()

        section_text = ""
        inside_section = False
        previous_line = ""
        for line in kernel_comments:

            if inside_section:

                if line.startswith("----"):
                    break

                if not previous_line.startswith("----"):
                    section_text += previous_line + "\n"

            elif previous_line.startswith(section_name) and line.startswith("----"):
                inside_section = True

            previous_line = line

        return section_text

    except Exception as ex:
        logging.error('Error on get_section_text_from_kernel_comments:', ex)
        return ""


def get_kernel_version(kernel_path):
    #
    # So far ExoMarsRSP is the only mission with 3 zeros in the version
    # number, that is why it is not generalised
    #
    if 'emrsp' in kernel_path:
        version_format = '{:03d}'
    else:
        version_format = '{:02d}'

    extension = str(os.path.splitext(kernel_path)[1]).lower()
    if extension2type(extension) == 'mk':
        version_format = '{:03d}'

    return version_format.format(int(kernel_path.split('.')[0][-2:]))
