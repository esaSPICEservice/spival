import os

import spiceypy
from spiceypy.utils.support_types import SpiceyError

from spival.utils.files import is_empty_file, \
                                has_badchars,\
                                exceeds_line_lengths, \
                                commnt_read, \
                                get_section_text_from_kernel_comments, \
                                get_kernel_version, \
                                validate_indentation, \
                                validate_trailing_chars


KERNEL_TEXT_EXTENSIONS = [".tf", ".ti", ".tls", ".tm", ".tpc", ".tsc"]
KERNEL_BINARY_EXTENSIONS = [".bc", ".bds", ".bpc", ".bsp"]
KERNEL_TEXT_HEADERS = {".tf": "KPL/FK",
                       ".ti": "KPL/IK",
                       ".tls": "KPL/LSK",
                       ".tm": "KPL/MK",
                       ".tpc": "KPL/PCK",
                       ".tsc": "KPL/SCLK"}
KERNEL_EXTENSIONS = KERNEL_TEXT_EXTENSIONS + KERNEL_BINARY_EXTENSIONS
COMMENTS_FILE_IGNORE_LINES = ["COMMENTS_FILE_NAME",
                              "INTERNAL_FILE_NAME",
                              "SCLK_FILE_NAME",
                              "LSK_FILE_NAME",
                              "FRAMES_FILE_NAME",
                              "FRAME_DEF_FILE",
                              "AEM2CK OUTPUT FILE",
                              "OEM2SPK OUTPUT FILE",
                              "SEG.SUMMARY",
                              "$KERNELS"]
HAS_VERSION_AND_DATE_SECTION_EXTENSIONS = [".tf", ".ti"]
CONTACT = "Alfredo Escalante Lopez"


# Modification of:
# https://spiceypy.readthedocs.io/en/main/other_stuff.html#lesson-1-kernel-management-with-the-kernel-subsystem
def write_mk_kernels_report(mk_path, out_report_file):

    # Prepare report file for writing
    out_file = open(out_report_file, 'w+')

    try:
        # Load the meta kernel then use KTOTAL to interrogate the SPICE
        # kernel subsystem.
        out_file.write('Loading MK: {0}\n'.format(mk_path))
        spiceypy.furnsh(mk_path)

        count = spiceypy.ktotal('ALL')
        out_file.write('Kernel count after load: {0}\n'.format(count))

        # Loop over the number of files; interrogate the SPICE system
        # with spiceypy.kdata for the kernel names and the type.
        # 'found' returns a boolean indicating whether any kernel files
        # of the specified type were loaded by the kernel subsystem.
        # This example ignores checking 'found' as kernels are known
        # to be loaded.
        for i in range(0, count):
            [file, ktype, source, handle] = spiceypy.kdata(i, 'ALL')
            out_file.write('File   {0}\n'.format(file))
            out_file.write('Type   {0}\n'.format(ktype))
            out_file.write('Source {0}\n\n'.format(source))

        # Lets write the first 1000 variables and their values
        cvals = spiceypy.gnpool("*", 0, 1000)
        for cval in cvals:

            #
            # Use spiceypy.dtpool to return the dimension and type,
            # C (character) or N (numeric), of each pool
            # variable name in the cvals array. We know the
            # kernel data exists.
            #
            [dim, type] = spiceypy.dtpool(cval)

            out_file.write('\n' + cval)
            out_file.write(' Number items: {0}   Of type: {1}\n'.format(dim, type))

            #
            # Test character equality, 'N' or 'C'.
            #
            if type == 'N':

                #
                # If 'type' equals 'N', we found a numeric array.
                # In this case any numeric array will be an array
                # of double precision numbers ('doubles').
                # spiceypy.gdpool retrieves doubles from the
                # kernel pool.
                #
                dvars = spiceypy.gdpool(cval, 0, 10)
                for dvar in dvars:
                    out_file.write('  Numeric value: {0:20.6f}\n'.format(dvar))

            elif type == 'C':

                #
                # If 'type' equals 'C', we found a string array.
                # spiceypy.gcpool retrieves string values from the
                # kernel pool.
                #
                cvars = spiceypy.gcpool(cval, 0, 10)

                for cvar in cvars:
                    out_file.write('  String value: {0}\n'.format(cvar))

            else:

                #
                # This block should never execute.
                #
                out_file.write('Unknown type. Code error.\n')

        # Now unload the meta kernel. This action unloads all
        # files listed in the meta kernel.
        spiceypy.unload(mk_path)

    except SpiceyError as err:
        out_file.write(str(err))

    # Done. Unload the kernels.
    spiceypy.kclear()

    return


def is_valid_kernel(kernel_file, check_line_length=True, check_indentation=True, check_trailing_chars=True):

    extension = str(os.path.splitext(kernel_file)[1]).lower()
    if extension in KERNEL_EXTENSIONS:

        if extension in KERNEL_TEXT_EXTENSIONS:
            if not is_valid_text_kernel(kernel_file,
                                        check_line_length, check_indentation, check_trailing_chars):
                print("ERROR!! - NOT A VALID TEXT KERNEL: " + kernel_file)
                return False

        else:
            # Is a binary kernel file, extract comments:
            if not is_valid_binary_kernel(kernel_file,
                                          check_line_length, check_indentation, check_trailing_chars):
                print("ERROR!! - NOT A VALID BINARY KERNEL: " + kernel_file)
                return False

        if extension == ".tm":
            if not is_valid_metakernel(kernel_file):
                print("ERROR!! - WRONG META-KERNEL: " + kernel_file)
                return False

    else:
        print("ERROR!! - NOT A KERNEL EXTENSION: " + extension + " for file " + kernel_file)
        return False

    return True


def is_valid_text_kernel(filename, check_line_length=True, check_indentation=True, check_trailing_chars=True):

    if not has_valid_text_kernel_header(filename):
        return False

    if not is_valid_comment_file(filename, check_line_length, check_indentation, check_trailing_chars):
        return False

    if not has_valid_version_and_date_section(filename):
        return False

    if not has_valid_contact_section(filename):
        return False

    # TODO: Continue implementation

    return True


def is_valid_comment_file(filename, check_line_length=True, check_indentation=True, check_trailing_chars=True):

    if is_empty_file(filename):
        print("ERROR!! - EMPTY FILE: " + filename)
        return False

    if has_badchars(filename):
        print("ERROR!! - HAS BAD CHARS: " + filename)
        return False

    if check_line_length:
        if exceeds_line_lengths(filename, ignore_lines=COMMENTS_FILE_IGNORE_LINES):
            print("ERROR!! - EXCEEDS LINE LENGTH: " + filename)
            return False

    if check_indentation:
        if validate_indentation(filename, indentation=3):
            print("ERROR!! - HAS WRONG INDENTATION: " + filename)
            return False

    if check_trailing_chars:
        if validate_trailing_chars(filename):
            print("ERROR!! - HAS TRAILING CHARS: " + filename)
            return False

    # TODO: Continue implementation

    return True


def is_valid_binary_kernel(filename, check_line_length=True, check_indentation=True, check_trailing_chars=True):
    extension = str(os.path.splitext(filename)[1]).lower()

    # Write comments to a fie
    comment_filename = filename.replace(extension, ".commnt")
    with open(comment_filename, 'w') as commnt_file:
        commnt_file.write(str(commnt_read(filename)))

    is_valid = is_valid_comment_file(comment_filename,
                                     check_line_length, check_indentation, check_trailing_chars)
    if not is_valid:
        print("ERROR!! - WRONG COMMENTS: " + filename)
    os.remove(comment_filename)

    if not has_valid_version_and_date_section(filename):
        return False

    if not has_valid_contact_section(filename):
        return False

    return is_valid


def is_valid_metakernel(mk_path):

    is_valid_mk = True
    prev_cwd = os.getcwd()

    try:
        # Load the meta kernel then use KTOTAL to interrogate the SPICE
        # kernel subsystem.
        abspath = os.path.abspath(mk_path)
        dname = os.path.dirname(abspath)
        mk_filename = os.path.basename(abspath)
        filename, extension = os.path.splitext(mk_filename)
        os.chdir(dname)
        spiceypy.furnsh(mk_filename)

        count = spiceypy.ktotal('ALL')

        # Loop over the number of files; interrogate the SPICE system
        # with spiceypy.kdata for the kernel names and the type.
        # 'found' returns a boolean indicating whether any kernel files
        # of the specified type were loaded by the kernel subsystem.
        # This example ignores checking 'found' as kernels are known
        # to be loaded.
        loaded_files = []
        for i in range(0, count):
            [k_file, ktype, source, handle] = spiceypy.kdata(i, 'ALL')
            k_filename = os.path.basename(k_file)
            if k_filename not in loaded_files:
                loaded_files.append(k_filename)
            else:
                print("ERROR: Duplicated kernel: " + str(k_file) + " in MK filename: " + mk_filename)
                is_valid_mk = False

        # Lets write the first 10000 variables and their values
        cvals = spiceypy.gnpool("*", 0, 10000)
        for cval in cvals:

            #
            # Use spiceypy.dtpool to return the dimension and type,
            # C (character) or N (numeric), of each pool
            # variable name in the cvals array. We know the
            # kernel data exists.
            #
            [dim, type] = spiceypy.dtpool(cval)

            #
            # Test character equality, 'N' or 'C'.
            #
            if type == 'N':

                #
                # If 'type' equals 'N', we found a numeric array.
                # In this case any numeric array will be an array
                # of double precision numbers ('doubles').
                # spiceypy.gdpool retrieves doubles from the
                # kernel pool.
                #
                dvars = spiceypy.gdpool(cval, 0, 10)

            elif type == 'C':

                #
                # If 'type' equals 'C', we found a string array.
                # spiceypy.gcpool retrieves string values from the
                # kernel pool.
                #
                cvars = spiceypy.gcpool(cval, 0, 10)

                if cval == "SKD_VERSION":
                    # Check filename aligned with SKD_VERSION for MKs with version
                    if not filename.endswith(str(cvars[0])) and "_v" in str(filename).lower():
                        print("ERROR: Variable SKD_VERSION: " + str(cvars[0]) +
                              " doesn't match MK filename: " + mk_filename)
                        is_valid_mk = False

                elif cval == "MK_IDENTIFIER":
                    if "_v" in str(filename).lower():
                        # Check filename aligned with MK_IDENTIFIER for MKs with version
                        if str(cvars[0]) != filename:
                            print("ERROR: Variable MK_IDENTIFIER: " + str(cvars[0]) +
                                  " doesn't match MK filename: " + mk_filename)
                            is_valid_mk = False
                    else:
                        # Check that an MK with name MK_IDENTIFIER exists in the MKs path
                        if not os.path.exists(str(cvars[0]) + extension):
                            print("ERROR: No MK with version found for MK_IDENTIFIER: " + str(cvars[0]) +
                                  " at MK filename: " + mk_filename)
                            is_valid_mk = False

            else:

                #
                # This block should never execute.
                #
                print("ERROR!! - WRONG META-KERNEL: Unknonw var type: " + str(type) +
                      " at variable " + str(cval) + " in mk: " + mk_path)
                is_valid_mk = False

        # Now unload the meta kernel. This action unloads all
        # files listed in the meta kernel.
        spiceypy.unload(mk_filename)

    except SpiceyError as err:
        print("ERROR!! - WRONG META-KERNEL: Raised exception: " + str(err) + " in mk: " + mk_path)
        is_valid_mk = False

    # Done. Unload the kernels.
    spiceypy.kclear()
    os.chdir(prev_cwd)

    return is_valid_mk


def has_valid_text_kernel_header(kernel_file):
    f = open(kernel_file).readlines()
    extension = str(os.path.splitext(kernel_file)[1]).lower()
    if not KERNEL_TEXT_HEADERS[extension] in f[0]:
        print('ERROR!! - WRONG KERNEL HEADER: ' + f[0] + " instead of " +
              KERNEL_TEXT_HEADERS[extension] + " for text kernel: " + kernel_file)
        return False

    return True


def has_valid_version_and_date_section(kernel_file):

    extension = str(os.path.splitext(kernel_file)[1]).lower()
    mandatory = extension in HAS_VERSION_AND_DATE_SECTION_EXTENSIONS

    text = get_section_text_from_kernel_comments(kernel_file, "Version and Date")
    if not len(text):
        if mandatory:
            print("ERROR: No 'Version and Date' section found in kernel: " + kernel_file)
            return False
        else:
            return True

    try:
        kernel_version = int(get_kernel_version(kernel_file))
    except Exception as ex:
        print("ERROR: Could not obtain kernel version from kernel: " + kernel_file)
        return False

    # Check that all defined versions in section are properly declared
    for line in text.splitlines():
        if line.strip().startswith("Version"):
            try:
                version = int(line.split("--")[0].strip().replace("Version", "").strip().replace(".", ""))

                if version > kernel_version:
                    print("ERROR: Version in 'Version and Date' section is greater than expected "
                          "in kernel: " + kernel_file + " , at line: " + line)
                    return False

                if version < kernel_version:
                    print("ERROR: Version in 'Version and Date' section is smaller than expected "
                          "in kernel: " + kernel_file + " , at line: " + line)
                    return False

                kernel_version = kernel_version - 1

            except Exception as ex:
                print("ERROR: Wrong version text format in 'Version and Date' section found in kernel: "
                      + kernel_file + " , at line: " + line)
                return False

    if kernel_version > -1:
        print("ERROR: Missing versions in 'Version and Date' section in kernel: " + kernel_file)
        return False

    return True


def has_valid_contact_section(kernel_file, mandatory=True):

    text = get_section_text_from_kernel_comments(kernel_file, "Contact Information")
    if not len(text):
        if mandatory:
            print("ERROR: No 'Contact Information' section found in kernel: " + kernel_file)
            return False
        else:
            return True

    if CONTACT not in text:
        print("ERROR: '" + CONTACT + "' not found in 'Contact Information' section in kernel: " + kernel_file)
        return False

    return True
