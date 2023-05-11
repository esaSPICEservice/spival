import hashlib
import os
import errno
import select
import shutil
import fileinput
import glob
import re
import logging
import subprocess
from datetime import datetime

from shutil import move, copyfile
from tempfile import mkstemp

from spival.utils.skd_val_logger import log_error, log_warn

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


def add_carriage_return(line):
    #
    # Adding CR to line
    #
    if '\r\n' not in line:
        line = line.replace('\n', '\r\n')
    if '\r\n' not in line:
        line += '\r\n'

    return line


def is_empty_file(file):
    return os.stat(file).st_size == 0


def is_valid_pds_filename(file_path):

    """
    Renaming Files
            The names of the files to be included in the archive must
            comply with the expanded ISO 9660 Level 2 requirement adopted
            by PDS. Thy must have 36.3 form -- 1-36 character long name +
            1-3 character long extension -- and must consist of letters
            (a-z), digits (0-9) and underscores (_). All names that don't
            comply with this requirement must be changed. NAIF recommends
            that the files are named using lowercase letters (as is done
            for the majority of the PDS-D data sets) rather than using
            upper case letters that were the requirement during the CD era.
    """

    max_filename_length = 36
    max_extension_length = 3
    valid_chars = "abcdefghijklmnopqrstuvwxyz_0123456789"

    is_valid_filename = True

    basename = os.path.basename(file_path)
    filename, extension = os.path.splitext(basename)

    if len(filename) > max_filename_length:
        log_error("INVALID_PDS_FILENAME",
                  "Filename: " + filename + " with length: " + str(len(filename))
                  + " exceeds maximum recommended length: " + str(max_filename_length), file_path)
        is_valid_filename = False

    extension = extension.replace(".", "")
    if len(extension) > max_extension_length:
        log_error("INVALID_PDS_FILENAME",
                  "File extension: " + extension + " with length: " + str(len(extension))
                  + " exceeds maximum recommended length: " + str(max_extension_length), file_path)
        is_valid_filename = False

    num_dot_found = 0
    has_invalid_chars = False
    for char in str(basename).lower():
        if char != ".":
            if char not in valid_chars:
                has_invalid_chars = True
        else:
            num_dot_found += 1

    if num_dot_found == 0:
        log_error("INVALID_PDS_FILENAME", "At least one '.' is required at filename: " + basename, file_path)
        is_valid_filename = False
    elif num_dot_found > 1:
        log_error("INVALID_PDS_FILENAME", "More than one '.' found at filename: " + basename, file_path)
        is_valid_filename = False

    if has_invalid_chars:
        log_error("INVALID_PDS_FILENAME", "Invalid chars found at filename. That must consist of letters (a-z), "
                                          "digits (0-9) and underscores (_) at : " + filename, file_path)
        is_valid_filename = False

    return is_valid_filename


def has_badchars(file_path):
    file = open(file_path, 'r')
    linen = 0
    badchars_detected = False
    for line in file.readlines():
        linen += 1
        for i in range(0, len(line), 1):
            e = line[i]
            if (re.sub('[ -~]', '', e)) != "" and e != '\n':
                log_error("BAD_CHAR", "NON ASCII CHAR: \'" + e + "\' detected at line: " + str(linen), file_path)
                badchars_detected = True

        for bad_char_keyword in BAD_CHAR_KEYWORDS:
            if bad_char_keyword in line:
                log_error("BAD_CHAR", " BAD_CHAR_KEYWORD found: \'" + bad_char_keyword +
                          "\' detected at line: " + str(linen), file_path)
                badchars_detected = True

    file.close()
    return badchars_detected


def exceeds_line_lengths(file, max_length=MAX_LINE_LENGTH, ignore_lines=None):

    if ignore_lines is None:
        ignore_lines = []

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
                log_error("EXCEEDS_LINE_LENGTH", f[i] + "\n Line nr: " + str(linen), file)
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
            log_warn("WRONG_INDENTATION", "WRONG INDENTATION: Line nr: " + str(linen) + "\n'" + line + "'", file)
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
            log_warn("TRAILING_CHARS", "Found " + str(trailing_chars) + " trailing char at Line nr: " +
                     str(linen) + "\n'" + line + "'", file)
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
    """Makes a folder if not present"""
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


def get_kernel_comments(kernel_path, directories=None):

    # First check if is a binary kernel or text kernel
    name, extension = os.path.splitext(kernel_path)
    if str(extension).lower().startswith(".t"):
        # Is a text kernel, just read the file:
        kernel_comments = read_all_text(kernel_path)
    else:
        # Shall be a binary kernel, use commnt read:
        kernel_comments = commnt_read(kernel_path, directories)

    return kernel_comments


def get_section_text_from_kernel_comments(kernel_path, section_name, directories=None):
    try:

        kernel_comments = get_kernel_comments(kernel_path, directories)
        kernel_comments = kernel_comments.splitlines()

        section_text = ""
        inside_section = False
        previous_line = ""
        for line in kernel_comments:

            if inside_section:

                if line.startswith("----") or line.startswith("===="):
                    break

                if not (previous_line.startswith("----") or previous_line.startswith("====")):
                    section_text += previous_line + "\n"

            elif previous_line.startswith(section_name) \
                    and (line.startswith("----") or line.startswith("====")):
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

    filename, extension = os.path.splitext(kernel_path)
    if extension2type(extension.lower()) == 'mk':
        version_format = '{:03d}'

    return version_format.format(int(filename[-2:]))


def files_are_equal(file1, file2):
    return md5(file1) == md5(file2)


def get_text_and_data_from_kernel(kernel_path):

    text = get_kernel_comments(kernel_path)

    inside_data_section = False
    data_text = ""
    comments = ""
    line_nr = 0

    for line in text.splitlines():

        striped_line = line.strip()

        if striped_line == '\\begintext':
            if inside_data_section:
                inside_data_section = False
            else:
                raise Exception("Found '\\begintext' without previous \\begindata at:  "
                                + kernel_path + " on line: " + str(line_nr))

        elif striped_line == '\\begindata':
            if not inside_data_section:
                inside_data_section = True
            else:
                raise Exception("Found '\\begindata' without previous \\begintext at:  "
                                + kernel_path + " on line: " + str(line_nr))

        elif inside_data_section:
            data_text += line + "\n"

        else:
            comments += line + "\n"

        line_nr += 1

    return data_text, comments


def get_sections_map_from_kernel_comments(kernel_comments):
    try:

        kernel_comments = kernel_comments.splitlines()

        sections_map = {}
        section_text = ""
        section_name = ""
        previous_line = ""

        for line in kernel_comments:

            if len(previous_line) > 0 \
                    and (line.startswith("----") or line.startswith("====")):

                # We have started a new section, store previous section and start new one
                if len(section_name) > 0:
                    sections_map[section_name] = section_text

                section_name = previous_line.strip()
                section_text = previous_line + "\n" + line + "\n"

            else:
                section_text += previous_line + "\n"

            previous_line = line

        if len(section_name) > 0:
            sections_map[section_name] = section_text

        return sections_map

    except Exception as ex:
        logging.error('Error on get_sections_map_from_kernel_comments:', ex)
        return None


def matches_string(input_str, match_pattern):
    # NOTE:
    # match_patter string could have one of the following syntax's:
    # @SW@text -> Checks input_str starts with text
    # @EW@text -> Checks input_str ends with text
    # @IN@text -> Checks input_str contains text
    # text -> Checks input_str is equal to text

    match_patterns = [match_pattern]
    if "||" in match_pattern:
        match_patterns = match_pattern.split("||")

    for pattern in match_patterns:
        pattern = str(pattern)

        if pattern.startswith("@SW@"):
            matched = input_str.startswith(pattern.replace("@SW@", ""))
        elif pattern.startswith("@EW@"):
            matched = input_str.endswith(pattern.replace("@EW@", ""))
        elif pattern.startswith("@IN@"):
            matched = pattern.replace("@IN@", "") in input_str
        else:
            matched = pattern == input_str

        if matched:
            return True

    return False


def get_section_from_sections_map(section_pattern, sections_map):
    for section_name in sections_map:
        if matches_string(section_name, section_pattern):
            return section_name, sections_map[section_name]

    return None, None


def get_naif_ids_from_text(text):
    naif_ids = {}

    naif_code_line = ""
    naif_name_line = ""

    for line in text.splitlines():
        if "NAIF_BODY_CODE" in line:
            if len(naif_code_line):
                raise Exception("Consecutive NAIF_BODY_CODE lines found: '" + naif_code_line + "' and '" + line + "'")
            naif_code_line = line

        if "NAIF_BODY_NAME" in line:
            if len(naif_name_line):
                raise Exception("Consecutive NAIF_BODY_NAME lines found: '" + naif_name_line + "' and '" + line + "'")
            naif_name_line = line

        if len(naif_code_line) and len(naif_name_line):

            body_name_parts = naif_name_line.split("'")
            if len(body_name_parts) != 3 \
                    or "=" not in naif_name_line:
                raise Exception("Wrong NAIF_BODY_NAME line format: " + naif_name_line)

            if "=" not in naif_code_line \
                    or len(naif_code_line.split("=")) != 2:
                raise Exception("Wrong NAIF_BODY_CODE line format: " + naif_code_line)

            try:
                body_name = naif_name_line.split("'")[1].strip()
                naif_id = int(naif_code_line.split("=")[1].replace("(", "").replace(")", "").strip())
            except Exception as ex:
                raise Exception("Wrong NAIF Association lines format: '"
                                + naif_code_line + "' and '" + naif_name_line + "' , ex: " + str(ex))

            if naif_id not in naif_ids:
                naif_ids[naif_id] = {"id": naif_id, "name": body_name, "synonyms": [body_name]}
            else:
                if body_name not in naif_ids[naif_id]["synonyms"]:
                    naif_ids[naif_id]["synonyms"].append(body_name)
                    naif_ids[naif_id]["name"] = body_name
                else:
                    raise Exception("Duplicated NAIF_BODY_NAME at line: " + naif_name_line)

            naif_code_line = ""
            naif_name_line = ""

    return naif_ids


def get_naif_ids_from_text_with_tables(text):

    """
        # TODO: CONTINUE IMPLEMENTATION, For the moment only works with tables of type, and with no empty lines.

       ---------------------  -------  --------------------------
       Name                   ID       Synonyms
      ---------------------  -------  --------------------------
       MPO                      -121   BEPICOLOMBO MPO,
                                       MERCURY PLANETARY ORBITER
       MPO_SPACECRAFT        -121000   MPO_SC
       MPO_SA                -121012

    """

    naif_ids = {}

    last_naif_id = None
    inside_table = False
    has_synonyms_column = False
    synonyms_column_index = -1
    previous_line = ""
    original_prev_line = ""
    for line in text.splitlines():

        original_line = line
        line = line.strip()

        if line.startswith("--------") and previous_line.lower().startswith("name"):

            prev_line_parts = previous_line.split()
            if len(prev_line_parts) > 1 \
                    and prev_line_parts[0].lower() == "name" \
                    and prev_line_parts[1].lower() == "id":
                inside_table = True

                if len(prev_line_parts) > 2:
                    if prev_line_parts[2].lower() == "synonyms":
                        has_synonyms_column = True
                        synonyms_column_index = original_prev_line.lower().index("synonyms") - 2  # -2 to give some extra margin if wrong indentation in synonyms
                    else:
                        raise Exception("Expected 'Synonyms' as third column of line: " + line)
                previous_line = line
                continue

        if inside_table:

            if not len(line) or line.startswith("--------"):
                inside_table = False
                previous_line = line
                continue

            try:
                if has_synonyms_column and last_naif_id is not None:
                    num_left_spaces = len(original_line) - len(original_line.lstrip())
                    if num_left_spaces >= synonyms_column_index:
                        # We are in a synonyms row
                        for syn in line.strip().split(","):
                            naif_ids[last_naif_id]["synonyms"].append(syn)
                        continue

                line_parts = line.split()
                body_name = line_parts[0].strip()
                if "*" in body_name:
                    # Ignore lines in table with *, such us: MPO_SERENA_ELENA_AN_NN*     -1215NN*
                    continue

                naif_id = int(line_parts[1].strip())

                synonyms = [body_name]
                if len(line_parts) > 2:
                    # We have synonyms
                    synonyms_text = line.split(str(naif_id))[1].strip()
                    for syn in synonyms_text.split(","):
                        synonyms.append(syn)

                naif_ids[naif_id] = {"id": naif_id, "name": body_name, "synonyms": synonyms}
                last_naif_id = naif_id
            except:
                raise Exception("Wrong NAIF ID table row format: " + line)

        previous_line = line
        original_prev_line = original_line

    return naif_ids


def get_frames_definitions_from_text(text):
    frames = {}
    frame_name2id = {}
    last_frame_id = None
    last_used_id = None
    curr_var = ""
    used_id = ""
    indent_break = False
    for line in text.splitlines():
        if "=" in line:
            tokens = line.split()
            curr_var = tokens[0].strip()
            curr_value = line.split("=")[1].strip()

            if curr_var.startswith("NAIF_") \
                    or curr_var.startswith("SCLK") \
                    or curr_var.startswith("OBJECT"):
                # Name to Id, SCLK or Object association line, ignore them
                continue

            if not tokens[1] == "=":
                raise Exception("Wrong line format: " + line)

            if len(tokens) < 3:
                raise Exception("Wrong line format: " + line)

            frame_id = None
            try:
                if curr_var.startswith("BODY"):
                    frame_id_s = curr_var.replace("BODY", "").split("_")[0]
                    if frame_id_s.replace("-", "").isnumeric():
                        # Get frame id from variable name: eg: BODY-28999_POLE_RA
                        frame_id = int(frame_id_s)
                        used_id = frame_id_s
                else:
                    frame_id_s = curr_var.split("_")[1]
                    if frame_id_s.replace("-", "").isnumeric():
                        # Get frame id from variable name: eg: FRAME_-121411_CLASS
                        frame_id = int(frame_id_s)
                        used_id = frame_id_s
                    else:
                        # Try to get frame id from the value field: Eg: FRAME_MPO_PHEBUS_PB = -121411
                        frame_id_s = curr_value
                        if frame_id_s.replace("-", "").isnumeric():
                            frame_id = int(frame_id_s)
                            used_id = frame_id_s
                        else:
                            # Look for frame name in variable name, Eg: TKFRAME_KIRUNA1_TOPO_UNITS
                            frame_name = "_".join(curr_var.split("_")[1:-1])
                            if frame_name in frame_name2id:
                                frame_id = frame_name2id[frame_name]
                                used_id = frame_name

            except Exception as ex:
                raise Exception("Wrong FRAME ID at line: '" + line + "' , ex: " + str(ex))

            if frame_id is None:
                raise Exception("FRAME ID not valid, at line: '" + line + "'")

            else:

                if frame_id not in frames:
                    if last_frame_id is not None:
                        # Remove blank lines at borders
                        frames[last_frame_id]["definition"] = frames[last_frame_id]["definition"].rstrip()

                    frames[frame_id] = {"id": frame_id,
                                        "definition": "",
                                        "keywords": {}}

                # Check if is a frame name line
                frame_var_parts = curr_var.split("_")
                if len(frame_var_parts) == 3 \
                        and frame_var_parts[0] == "FRAME" and frame_var_parts[2] == "NAME":
                    frame_name = curr_value.replace("'", "").strip()
                    frames[frame_id]["name"] = frame_name
                    frame_name2id[frame_name] = frame_id

                if not frames[frame_id]["definition"].endswith("\n"):
                    frames[frame_id]["definition"] += "\n"
                frames[frame_id]["definition"] += line + "\n"

                keyword = curr_var
                if keyword.endswith("_NAME"):
                    keyword = keyword.replace(used_id, "{id}")
                elif used_id in keyword and len(keyword.split(used_id)[1]):
                    keyword = keyword.replace(used_id, "{used_id}")
                else:
                    keyword = "FRAME_{name}"

                if keyword not in frames[frame_id]["keywords"]:

                    if keyword.endswith("_CLASS"):
                        frames[frame_id]["frame_class"] = curr_value

                    keyword_data = {
                                    "keyword": keyword,
                                    "used_id": used_id,
                                    "var": curr_var,
                                    "value": curr_value,
                                    "line_nr": len(frames[frame_id]["keywords"]),
                                    "keyword_indent": line.index(curr_var),
                                    "equal_indent": line.index("="),
                                    "value_indent": line.replace(curr_var, "#" * len(curr_var)).index(tokens[2]),
                                    "indent_break": indent_break,
                                    "line": line
                                    }

                    frames[frame_id]["keywords"][keyword] = keyword_data

                else:
                    raise Exception("Duplicated keyword: " + curr_var + " at line: '" + line)

                last_frame_id = frame_id
                last_used_id = used_id
                indent_break = False

        elif len(line.strip()):
            # We could be at matrix definition so, line shall contain numbers and or ")"
            # It also could be and _ALIGNED_WITH keyword definition, in such case the shall be a string between ''
            if last_frame_id is not None:

                if curr_var == "TKFRAME_" + str(last_used_id) + "_MATRIX" \
                        or curr_var == "TKFRAME_" + str(last_used_id) + "_ANGLES" \
                        or curr_var == "TKFRAME_" + str(last_used_id) + "_Q" \
                        or curr_var == "TKFRAME_" + str(last_used_id) + "_AXES" \
                        or (curr_var.startswith("FRAME_" + str(last_used_id) + "_ANGLE_")
                            and curr_var.endswith("_COEFFS")):

                    # SHALL BE A VECTOR DEFINITION
                    arr = line.replace(",", " ").replace(")", " ").split()
                    # If there are tokens, shall be numbers
                    for elem in arr:
                        try:
                            value = float(elem.strip())
                        except:
                            raise Exception("Wrong number found: " + elem + "  for TKFRAME_..._MATRIX at line: " + line)

                    if not len(arr) and line.strip() != ")":
                        # If no tokens found, only ")" is supported
                        raise Exception("Unexpected line in frame definition: for TKFRAME_..._MATRIX for '"
                                        + line + "' shall be: ')'")

                elif curr_var == "FRAME_" + str(last_frame_id) + "_ALIGNED_WITH":

                    # SHALL BE AN ALIGNED_WITH
                    if len(line.split("'")) != 3 and line.strip() != ")":
                        raise Exception("Unexpected line in frame definition: '" + line +
                                        "' for FRAME_..._ALIGNED_WITH")

                elif not curr_var.startswith("BODY") \
                        and not curr_var.startswith("SCLK"):
                    raise Exception("Unexpected line in frame definition: '" + line + "' " +
                                    "for frame_id: " + str(last_frame_id))

                frames[last_frame_id]["definition"] += line + "\n"

                keyword = curr_var
                if last_used_id in keyword and len(keyword.split(used_id)[1]):
                    keyword = keyword.replace(used_id, "{used_id}")
                    text = frames[last_frame_id]["keywords"][keyword]["value"]
                    if len(text.splitlines()) == 1:
                        text = text + "\n"

                    text += line + "\n"
                    frames[last_frame_id]["keywords"][keyword]["value"] = text

            else:
                raise Exception("Unexpected line in frame definition: '" + line + "'")

        elif last_frame_id is not None:
            # Just un case there are blank lines, link them to the definition for later checks
            frames[last_frame_id]["definition"] += line + "\n"

            # Notify that equal indentation or value indentation could be changed
            indent_break = True

    if last_frame_id is not None:
        # Remove blank lines at borders
        frames[last_frame_id]["definition"] = frames[last_frame_id]["definition"].rstrip()

    return frames


def get_instruments_definitions_from_text(text):
    instruments = {}
    instrument_name2id = {}
    last_ins_id = None
    curr_var = ""
    indent_break = False
    for line in text.splitlines():
        if "=" in line:
            tokens = line.split()
            curr_var = tokens[0].strip()
            curr_value = line.split("=")[1].strip()

            if curr_var.startswith("NAIF_") \
                   or curr_var.startswith("SCLK") \
                   or curr_var.startswith("OBJECT"):
                continue  # Name to Id, SCLK or Object association line, ignore them

            if not tokens[1] == "=":
                raise Exception("Wrong line format: " + line)

            ins_id = None
            try:
                ins_id_s = curr_var.split("_")[0].replace("INS", "")
                if ins_id_s.replace("-", "").isnumeric():
                    # Get frame id from variable name: eg: INS-121310_NAME
                    ins_id = int(ins_id_s)
            except Exception as ex:
                raise Exception("Wrong INSTRUMENT ID at line: '" + line + "' , ex: " + str(ex))

            if ins_id is None:
                raise Exception("INSTRUMENT ID not valid, at line: '" + line + "'")

            else:

                if ins_id not in instruments:
                    if last_ins_id is not None:
                        # Remove blank lines at borders
                        instruments[last_ins_id]["definition"] = instruments[last_ins_id]["definition"].rstrip()

                    instruments[ins_id] = {"id": ins_id,
                                            "definition": "",
                                            "keywords": {}}

                # Check if is a instrument name line
                if curr_var.endswith("NAME"):
                    ins_name = curr_value.replace("'", "").strip()
                    instruments[ins_id]["name"] = ins_name
                    instrument_name2id[ins_name] = ins_id

                if not instruments[ins_id]["definition"].endswith("\n"):
                    instruments[ins_id]["definition"] += "\n"
                instruments[ins_id]["definition"] += line + "\n"

                keyword = curr_var.replace(str(ins_id), "{id}")

                if keyword not in instruments[ins_id]["keywords"]:

                    if keyword.endswith("_FOV_SHAPE"):
                        instruments[ins_id]["fov_shape"] = curr_value.replace("'", "").strip()

                    keyword_data = {
                                    "keyword": keyword,
                                    "id": ins_id,
                                    "var": curr_var,
                                    "value": curr_value,
                                    "line_nr": len(instruments[ins_id]["keywords"]),
                                    "keyword_indent": line.index(curr_var),
                                    "equal_indent": line.index("="),
                                    "value_indent": line.replace(curr_var, "#" * len(curr_var)).index(tokens[2]),
                                    "indent_break": indent_break,
                                    "line": line
                                    }

                    instruments[ins_id]["keywords"][keyword] = keyword_data

                else:
                    raise Exception("Duplicated keyword: " + curr_var + " at line: '" + line)

                last_ins_id = ins_id
                indent_break = False

        elif len(line.strip()):
            # We could be at matrix definition so, line shall contain numbers and or ")"
            if last_ins_id is not None:

                instruments[last_ins_id]["definition"] += line + "\n"

                keyword = curr_var
                if str(last_ins_id) in keyword and len(keyword.split(str(last_ins_id))[1]):
                    keyword = curr_var.replace(str(last_ins_id), "{id}")
                    text = instruments[last_ins_id]["keywords"][keyword]["value"]
                    if len(text.splitlines()) == 1:
                        text = text + "\n"

                    text += line + "\n"
                    instruments[last_ins_id]["keywords"][keyword]["value"] = text

            else:
                raise Exception("Unexpected line in instrument definition: '" + line + "'")

        elif last_ins_id is not None:
            # Just un case there are blank lines, link them to the definition for later checks
            instruments[last_ins_id]["definition"] += line + "\n"

            # Notify that equal indentation or value indentation could be changed
            indent_break = True

    if last_ins_id is not None:
        # Remove blank lines at borders
        instruments[last_ins_id]["definition"] = instruments[last_ins_id]["definition"].rstrip()

    return instruments


def get_sites_definitions_from_text(text):
    sites = {}
    curr_site_name = None
    last_site_name = None
    for line in text.splitlines():
        if "=" in line:
            tokens = line.replace("+=", "=").split()
            curr_var = tokens[0].strip()
            curr_value = line.split("=")[1].strip()

            if not tokens[1] == "=":
                raise Exception("Wrong line format: " + line)

            try:
                if curr_var == "SITES":
                    curr_value_parts = curr_value.split("'")
                    if len(curr_value_parts) == 3 \
                            and "(" in curr_value_parts[0] \
                            and len(curr_value_parts[1]) \
                            and ")" in curr_value_parts[2]:

                        # Get site name from value
                        curr_site_name = curr_value_parts[1]
                    else:
                        raise Exception("Wrong SITES format: " + line)

            except Exception as ex:
                raise Exception("Wrong SITES at line: '" + line + "' , ex: " + str(ex))

            if curr_site_name is None:
                raise Exception("SITE NAME not set, at line: '" + line + "'")

            else:

                if curr_site_name not in sites:
                    if last_site_name is not None \
                            and curr_site_name != last_site_name:
                        # Remove blank lines at borders
                        sites[last_site_name]["definition"] = sites[last_site_name]["definition"].rstrip()
                        last_site_name = curr_site_name

                    sites[curr_site_name] = {"name": curr_site_name,
                                             "definition": "",
                                             "keywords": {}}

                if not sites[curr_site_name]["definition"].endswith("\n"):
                    sites[curr_site_name]["definition"] += "\n"
                sites[curr_site_name]["definition"] += line + "\n"

                keyword = curr_var.replace(curr_site_name, "{name}")

                if keyword not in sites[curr_site_name]["keywords"]:

                    keyword_data = {
                                    "keyword": keyword,
                                    "var": curr_var,
                                    "value": curr_value,
                                    "line_nr": len(sites[curr_site_name]["keywords"]),
                                    "keyword_indent": line.index(curr_var),
                                    "equal_indent": line.index("="),
                                    "value_indent": line.replace(curr_var, "#" * len(curr_var)).index(tokens[2]),
                                    "line": line
                                    }

                    sites[curr_site_name]["keywords"][keyword] = keyword_data

                else:
                    raise Exception("Duplicated keyword: " + curr_var + " at line: '" + line)

        elif len(line.strip()):
            raise Exception("Unexpected line in sites definition: '" + line + "'")

        elif curr_site_name is not None:
            # Just un case there are blank lines, link them to the definition for later checks
            sites[curr_site_name]["definition"] += line + "\n"

    if last_site_name is not None:
        # Remove blank lines at borders
        sites[last_site_name]["definition"] = sites[last_site_name]["definition"].rstrip()

    return sites
