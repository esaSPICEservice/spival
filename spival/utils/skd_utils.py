import os

import spiceypy
from spiceypy.utils.exceptions import NotFoundError
from spiceypy.utils.support_types import SpiceyError

from spival.utils.skd_constants import *
from spival.utils.files import is_empty_file, \
    has_badchars, \
    exceeds_line_lengths, \
    commnt_read, \
    get_section_text_from_kernel_comments, \
    get_kernel_version, \
    validate_indentation, \
    validate_trailing_chars, read_all_text, get_text_and_data_from_kernel, get_sections_map_from_kernel_comments, \
    get_section_from_sections_map, get_naif_ids_from_text, \
    get_frames_definitions_from_text, get_instruments_definitions_from_text, get_sites_definitions_from_text

# Modification of:
# https://spiceypy.readthedocs.io/en/main/other_stuff.html#lesson-1-kernel-management-with-the-kernel-subsystem
from spival.utils.skd_val_logger import log_error, log_info, log_warn

FOUND_NAIF_IDS = []
FOUND_FRAME_IDS = []
FOUND_FRAME_NAMES = []


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
    is_valid = True

    extension = str(os.path.splitext(kernel_file)[1]).lower()
    if extension in KERNEL_EXTENSIONS:

        if extension in KERNEL_TEXT_EXTENSIONS:
            if not is_valid_text_kernel(kernel_file,
                                        check_line_length, check_indentation, check_trailing_chars):
                log_error("INVALID_TEXT_KERNEL", "Invalid text kernel.", kernel_file)
                is_valid = False

        else:
            # Is a binary kernel file, extract comments:
            if not is_valid_binary_kernel(kernel_file,
                                          check_line_length, check_indentation, check_trailing_chars):
                log_error("INVALID_BINARY_KERNEL", "Invalid binary kernel.", kernel_file)
                is_valid = False

        if is_mk_file(kernel_file):
            if not is_valid_metakernel(kernel_file):
                log_error("INVALID_METAKERNEL", "Invalid meta-kernel.", kernel_file)
                is_valid = False

    else:
        log_error("WRONG_KERNEL_EXTENSION", "Invalid kernel extension: " + extension, kernel_file)
        is_valid = False

    return is_valid


def is_valid_text_kernel(filename, check_line_length=True, check_indentation=True, check_trailing_chars=True):
    is_valid = True

    if not has_valid_text_kernel_header(filename):
        is_valid = False

    if not is_valid_comment_file(filename, check_line_length, check_indentation, check_trailing_chars):
        is_valid = False

    if not has_valid_version_and_date_section(filename):
        is_valid = False

    if not has_valid_contact_section(filename):
        is_valid = False

    if is_fk_file(filename):
        if not is_valid_frames_kernel(filename):
            log_error("INVALID_FRAMES_KERNEL", "Invalid frames kernel.", filename)
            is_valid = False

    elif is_ik_file(filename):
        if not is_valid_instruments_kernel(filename):
            log_error("INVALID_INSTRUMENTS_KERNEL", "Invalid instruments kernel.", filename)
            is_valid = False

    # TODO: Do specific checks for text PCKs and SCLKs

    return is_valid


def is_valid_comment_file(filename, check_line_length=True, check_indentation=True, check_trailing_chars=True):

    if is_empty_file(filename):
        log_error("EMPTY_FILE", "File comments are empty", filename)
        return False

    is_valid = True
    if has_badchars(filename):
        log_error("HAS_BAD_CHARS", "Has bad chars.", filename)
        is_valid = False

    if check_line_length:
        if exceeds_line_lengths(filename, ignore_lines=COMMENTS_FILE_IGNORE_LINES):
            log_error("HAS_LONG_LINES", "Has long lines.", filename)
            is_valid = False

    if check_indentation:
        if validate_indentation(filename, indentation=3):
            log_error("HAS_WRONG_INDENTATION", "Has wrong indentation.", filename)
            is_valid = False

    if check_trailing_chars:
        if validate_trailing_chars(filename):
            log_error("HAS_TRAILING_CHARS", "Has trailing chars.", filename)
            is_valid = False

    # TODO: Continue implementation

    return is_valid


def is_valid_binary_kernel(filename, check_line_length=True, check_indentation=True, check_trailing_chars=True):
    extension = str(os.path.splitext(filename)[1]).lower()

    # Write comments to a fie
    comment_filename = filename.replace(extension, ".commnt")
    with open(comment_filename, 'w') as commnt_file:
        commnt_file.write(str(commnt_read(filename)))

    is_valid = is_valid_comment_file(comment_filename,
                                     check_line_length, check_indentation, check_trailing_chars)
    os.remove(comment_filename)

    if not has_valid_version_and_date_section(filename):
        is_valid = False

    if not has_valid_contact_section(filename):
        is_valid = False

    if is_spk_file(filename):
        if not is_valid_spk_kernel(filename):
            log_error("INVALID_SPK_KERNEL", "Invalid SPK kernel.", filename)
            is_valid = False

    elif is_ck_file(filename):
        if not is_valid_ck_kernel(filename):
            log_error("INVALID_CK_KERNEL", "Invalid CK kernel.", filename)
            is_valid = False

    # TODO: Do specific checks for Binary PCKs

    return is_valid


def is_valid_metakernel(mk_path):

    is_valid_mk = True
    prev_cwd = os.getcwd()

    abspath = os.path.abspath(mk_path)
    dname = os.path.dirname(abspath)
    mk_filename = os.path.basename(abspath)

    try:
        # Load the meta kernel then use KTOTAL to interrogate the SPICE
        # kernel subsystem.
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
                log_error("WRONG_MK", "Duplicated kernel: " + str(k_file) + " in MK", mk_filename)
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
                    if is_versioned_mk(mk_filename):
                        if not filename.endswith(str(cvars[0])):
                            log_error("WRONG_MK", "Variable SKD_VERSION: " + str(cvars[0]) +
                                      " doesn't match MK filename: " + mk_filename, mk_filename)
                            is_valid_mk = False
                    else:
                        # Check that an MK with name MK_IDENTIFIER exists in the MKs path
                        related_mk = filename + "_" + str(cvars[0]) + extension
                        if not os.path.exists(related_mk):
                            log_error("WRONG_MK", "No MK ( " + related_mk + " ) with version found for "
                                      "SKD_VERSION: " + str(cvars[0]) + " at MK filename: " + mk_filename, mk_filename)
                            is_valid_mk = False

                elif cval == "MK_IDENTIFIER":
                    if is_versioned_mk(mk_filename):
                        # Check filename aligned with MK_IDENTIFIER for MKs with version
                        if str(cvars[0]) != filename:
                            log_error("WRONG_MK", "Variable MK_IDENTIFIER: " + str(cvars[0]) +
                                        " doesn't match MK filename: " + mk_filename, mk_filename)
                            is_valid_mk = False
                    else:
                        # Check that an MK with name MK_IDENTIFIER exists in the MKs path
                        related_mk = str(cvars[0]) + extension
                        if not os.path.exists(related_mk):
                            log_error("WRONG_MK", "No MK ( " + related_mk + " ) with version found for "
                                        "MK_IDENTIFIER: " + str(cvars[0]) + " at MK filename: " + mk_filename,
                                      mk_filename)
                            is_valid_mk = False

            else:

                #
                # This block should never execute.
                #
                log_error("WRONG_MK", "Unknown var type: " + str(type) + " at variable " + str(cval), mk_filename)
                is_valid_mk = False

        # Now unload the meta kernel. This action unloads all
        # files listed in the meta kernel.
        spiceypy.unload(mk_filename)

    except SpiceyError as err:
        log_error("WRONG_MK", "Raised exception: " + str(err) + " in mk: " + mk_path, mk_filename)
        is_valid_mk = False

    # Done. Unload the kernels.
    spiceypy.kclear()
    os.chdir(prev_cwd)

    return is_valid_mk


def has_valid_text_kernel_header(kernel_file):
    f = open(kernel_file).readlines()
    extension = str(os.path.splitext(kernel_file)[1]).lower()
    if not KERNEL_TEXT_HEADERS[extension] in f[0]:
        log_error("WRONG_KERNEL_HEADER", "WRONG KERNEL HEADER: " + f[0] + " instead of " +
                    KERNEL_TEXT_HEADERS[extension] + " for text kernel: " + kernel_file, kernel_file)
        return False

    return True


def has_valid_version_and_date_section(kernel_file):

    extension = str(os.path.splitext(kernel_file)[1]).lower()
    mandatory = extension in HAS_VERSION_AND_DATE_SECTION_EXTENSIONS

    if extension == ".tsc":
        if "_v" not in os.path.basename(kernel_file).lower():
            # Ignore this check for SCLK Kernels with no version in the filename, such as: integral_fict_20220208.tsc
            return True

    text = get_section_text_from_kernel_comments(kernel_file, "Version and Date")
    if not len(text):
        if mandatory:
            log_error("WRONG_VERSION_SECTION", "No 'Version and Date' section found in kernel: " + kernel_file,
                      kernel_file)
            return False
        else:
            return True

    multiplier = 1
    try:
        kernel_version = int(get_kernel_version(kernel_file))
        if "_v" not in os.path.basename(kernel_file).lower():
            # In case that filenames has the form: rssd0003.tf or similar, we need to multiply
            # the version by 10 because in 'Version and Date' section shall appear like 3.0 -> 30
            multiplier = 10
    except Exception as ex:
        log_error("WRONG_VERSION_SECTION", "Could not obtain kernel version from kernel: " + kernel_file
                  + " , ex: " + str(ex), kernel_file)
        return False

    tmp_kernel_version = kernel_version * multiplier
    # Check that all defined versions in section are properly declared
    for line in text.splitlines():
        if line.strip().startswith("Version"):

            if "-draft" in line:
                # Ignore draft versions
                continue

            try:
                version = int(line.split("--")[0].strip().replace("Version", "").strip().replace(".", ""))

                if version > tmp_kernel_version:
                    log_error("WRONG_VERSION_SECTION",
                              "Version in 'Version and Date' section is greater than expected "
                                "in kernel: " + kernel_file + " with version: " + str(kernel_version)
                                + ", at line: " + line, kernel_file)
                    return False

                if version < tmp_kernel_version:
                    log_error("WRONG_VERSION_SECTION",
                              "Version in 'Version and Date' section is smaller than expected "
                                "in kernel: " + kernel_file + " with version: " + str(kernel_version)
                                + ", at line: " + line, kernel_file)
                    return False

                tmp_kernel_version = tmp_kernel_version - multiplier

            except Exception:
                log_error("WRONG_VERSION_SECTION",
                          "Wrong version text format in 'Version and Date' section found in kernel: "
                          + kernel_file + " with version: " + str(kernel_version) + ", at line: " + line, kernel_file)
                return False

    if tmp_kernel_version > -1:
        log_error("WRONG_VERSION_SECTION",
                  "Missing versions in 'Version and Date' section in kernel: " + kernel_file, kernel_file)
        return False

    return True


def has_valid_contact_section(kernel_file, mandatory=True):

    text = get_section_text_from_kernel_comments(kernel_file, "Contact Information")
    if not len(text):
        if mandatory:
            log_error("WRONG_CONTACT", "No 'Contact Information' section found", kernel_file)
            return False
        else:
            return True

    if CONTACT not in text:
        log_error("WRONG_CONTACT", "'" + CONTACT + "' not found in 'Contact Information' section", kernel_file)
        return False

    return True


def get_skd_version(skd_path):

    version_file = os.path.join(skd_path, "version")
    if not os.path.exists(version_file):
        raise Exception("Version file not found at path: " + version_file)

    version = read_all_text(version_file).strip()
    if len(version) != 4 or not version.startswith("v"):
        raise Exception("Wrong formatted version: '" + version + "' found at: " + version_file)

    return version


def has_extension(path, extension):
    fk_filename = os.path.basename(path)
    return str(os.path.splitext(fk_filename)[1]).lower() == extension


def is_fk_file(path):
    return has_extension(path, ".tf")


def is_ik_file(path):
    return has_extension(path, ".ti")


def is_mk_file(path):
    return has_extension(path, ".tm")


def is_spk_file(path):
    return has_extension(path, ".bsp")


def is_ck_file(path):
    return has_extension(path, ".bc")


def is_versioned_mk(mk_path):
    mk_filename = os.path.basename(mk_path)
    if not is_mk_file(mk_path):
        raise Exception("File is not a meta-kernel file: " + mk_path)

    return "_v" in str(os.path.splitext(mk_filename)[0]).lower() and not is_local_mk(mk_path)


def is_local_mk(mk_path):
    if not is_mk_file(mk_path):
        raise Exception("File is not a meta-kernel file: " + mk_path)

    return str(os.path.splitext(mk_path)[0]).lower().endswith("local")


def get_versions_history_from_release_notes_file(rel_notes_file):

    text = get_section_text_from_kernel_comments(rel_notes_file, "Appendix: Release History")
    if not len(text):

        text = get_section_text_from_kernel_comments(rel_notes_file, "Release History")
        if not len(text):
            log_error("WRONG_RELEASE_NOTES",
                      "No 'Release History' section found in kernel: " + rel_notes_file, rel_notes_file)
            return None

    versions = []
    # Check that all defined versions in section are properly declared
    indentation = -1
    for line in text.splitlines():
        if indentation < 0:
            if len(line.strip()) > 0:
                indentation = len(line) - len(line.lstrip())

        if indentation >= 0:
            if len(line) - len(line.lstrip()) == indentation:
                tokens = line.strip().split(" ")
                if len(tokens) == 4:
                    if tokens[3].startswith("v") and len(tokens[3].split(".")) == 3:
                        versions.append(tokens[3])

    return versions


def check_release_notes_version(rel_notes_file):

    basename = os.path.basename(rel_notes_file)
    filename, extension = os.path.splitext(basename)

    text = read_all_text(rel_notes_file)
    first_line = text.splitlines()[0]
    version = first_line.split()[-1]

    is_valid = True
    if not filename.endswith("skd_current"):
        if not filename.endswith("_skd_" + version.replace("v", "").replace(".", "")):
            log_error("WRONG_RELEASE_NOTES",
                      "Filename versions: " + rel_notes_file + " doesn't match the version: " + version
                        + " at line: " + first_line, rel_notes_file)
            is_valid = False

    # First paragraph shall contain "(version)"
    ver_text = "(" + version.replace("v", "") + ")"
    if ver_text not in text:
        log_error("WRONG_RELEASE_NOTES", "Text : " + ver_text + " not found in first paragraph.", rel_notes_file)
        is_valid = False

    notes = get_section_text_from_kernel_comments(rel_notes_file, "Notes")
    if not len(notes):
        log_error("WRONG_RELEASE_NOTES", "No 'Notes' section found in kernel.", rel_notes_file)

    elif version not in notes:
        log_error("WRONG_RELEASE_NOTES", "Version : " + version + " not found in Notes section.", rel_notes_file)
        is_valid = False

    return is_valid


def is_valid_frames_kernel(fk_path):

    try:
        data_text, comments = get_text_and_data_from_kernel(fk_path)
    except Exception as ex:
        log_error("DATA_AND_COMMENTS",
                  "Obtaining data text from: " + fk_path + " , exception: " + str(ex), fk_path)
        return False

    if not len(data_text):
        log_error("DATA_AND_COMMENTS",
                  "No data sections found in kernel: " + fk_path, fk_path)
        return False

    if not len(comments):
        log_error("DATA_AND_COMMENTS",
                  "No text comments found in kernel: " + fk_path, fk_path)
        return False

    # Don't continue if is a PINPOINT FK
    if "This file was created by PINPOINT." in comments:
        log_info("DATA_AND_COMMENTS",
                  "Not all FK checks were performed because is a PINPOINT FK: " + fk_path, fk_path)
        return True

    sections_map = get_sections_map_from_kernel_comments(comments)
    if sections_map is None:
        log_error("DATA_AND_COMMENTS",
                  "Could not obtain sections from kernel: " + fk_path, fk_path)
        return False

    # Check required sections
    all_required_section_found = check_required_sections(sections_map, REQUIRED_SECTIONS["FK"], fk_path)

    # Check NAIF IDs if any is found
    valid_ids = check_naif_id_associations(data_text, sections_map, fk_path)

    # Check frames definitions
    valid_frames = check_frame_definitions(data_text, sections_map, fk_path)

    return all_required_section_found and valid_ids and valid_frames


def is_valid_instruments_kernel(ik_path):

    try:
        data_text, comments = get_text_and_data_from_kernel(ik_path)
    except Exception as ex:
        log_error("DATA_AND_COMMENTS",
                  "Obtaining data text from: " + ik_path + " , exception: " + str(ex), ik_path)
        return False

    if not len(data_text):
        log_error("DATA_AND_COMMENTS",
                  "No data sections found in kernel: " + ik_path, ik_path)
        return False

    if not len(comments):
        log_error("DATA_AND_COMMENTS",
                  "No text comments found in kernel: " + ik_path, ik_path)
        return False

    sections_map = get_sections_map_from_kernel_comments(comments)
    if sections_map is None:
        log_error("DATA_AND_COMMENTS",
                  "Could not obtain sections from kernel: " + ik_path, ik_path)
        return False

    # Check required sections
    all_required_section_found = check_required_sections(sections_map, REQUIRED_SECTIONS["IK"], ik_path)

    # Check NAIF IDs if any is found
    valid_ids = check_naif_id_associations(data_text, sections_map, ik_path)

    # Check instruments definitions
    valid_instruments = check_instruments_definitions(data_text, sections_map, ik_path)

    return all_required_section_found and valid_ids and valid_instruments


def is_valid_spk_kernel(spk_path):

    try:
        data_text, comments = get_text_and_data_from_kernel(spk_path)
    except Exception as ex:
        log_error("DATA_AND_COMMENTS",
                  "Obtaining data text from: " + spk_path + " , exception: " + str(ex), spk_path)
        return False

    if not len(comments):
        log_error("DATA_AND_COMMENTS",
                  "No text comments found in kernel: " + spk_path, spk_path)
        return False

    if len(data_text):

        sections_map = get_sections_map_from_kernel_comments(comments)
        if sections_map is None:
            log_error("DATA_AND_COMMENTS",
                      "Could not obtain sections from kernel: " + spk_path, spk_path)
            return False

        if get_section_from_sections_map("@IN@PINPOINT", sections_map)[0] is not None:
            # Is a PINPOINT Kernel file

            # Check required sections
            all_required_section_found = check_required_sections(sections_map,
                                                                 REQUIRED_SECTIONS["SPK_PINPOINT"],
                                                                 spk_path)

            # Check sites definitions
            valid_sites = check_sites_definitions(data_text, sections_map, spk_path)

            return all_required_section_found and valid_sites

        elif get_section_from_sections_map("@IN@OEM2SPK", sections_map)[0] is not None:
            # Is a OEM2SPK Kernel file

            # Check required sections
            all_required_section_found = check_required_sections(sections_map,
                                                                 REQUIRED_SECTIONS["SPK_OEM2SPK"],
                                                                 spk_path)
            return all_required_section_found

        elif get_section_from_sections_map("@IN@MKSPK", sections_map)[0] is not None:
            # Is a MKSPK Kernel file

            # Check required sections
            all_required_section_found = check_required_sections(sections_map,
                                                                 REQUIRED_SECTIONS["SPK_MKSPK"],
                                                                 spk_path)
            return all_required_section_found

        else:
            log_error("DATA_AND_COMMENTS",
                      "SPK type not supported: " + spk_path, spk_path)
            return False

    else:
        # The SPK doesn't have /begindata sections, such as some NAIF SPKs and similar.
        return True


def is_valid_ck_kernel(ck_path):

    try:
        data_text, comments = get_text_and_data_from_kernel(ck_path)
    except Exception as ex:
        log_error("DATA_AND_COMMENTS",
                  "Obtaining data text from: " + ck_path + " , exception: " + str(ex), ck_path)
        return False

    if not len(comments):
        log_error("DATA_AND_COMMENTS",
                  "No text comments found in kernel: " + ck_path, ck_path)
        return False

    sections_map = get_sections_map_from_kernel_comments(comments)
    if sections_map is None:
        log_error("DATA_AND_COMMENTS",
                  "Could not obtain sections from kernel: " + ck_path, ck_path)
        return False

    if get_section_from_sections_map("@IN@orientation", sections_map)[0] is not None:
        # Is a Fixed attitude CK
        all_required_section_found = check_required_sections(sections_map,
                                                             REQUIRED_SECTIONS["CK_FIXED"],
                                                             ck_path)
        return all_required_section_found

    elif get_section_from_sections_map("Directions", sections_map)[0] is not None\
            or get_section_from_sections_map("Orientations", sections_map)[0] is not None\
            or get_section_from_sections_map("Schedule", sections_map)[0] is not None:
        # Is a predickt CK
        all_required_section_found = check_required_sections(sections_map,
                                                             REQUIRED_SECTIONS["CK_PREDICKT"],
                                                             ck_path)
        return all_required_section_found

    else:
        # Check required sections
        all_required_section_found = check_required_sections(sections_map,
                                                             REQUIRED_SECTIONS["CK"],
                                                             ck_path)
        return all_required_section_found


def check_required_sections(sections_map, required_sections, file_path):
    all_required_section_found = True

    for section_name in required_sections:
        sec_name, sec_text = get_section_from_sections_map(section_name, sections_map)

        if sec_name is None:
            log_error("MISSING_SECTION",
                      "Required section not found: '" + section_name + "' at " + file_path, file_path)
            all_required_section_found = False

        if not len(str(sec_text).strip()):
            log_error("MISSING_SECTION",
                      "Required section is empty: '" + section_name + "' at " + file_path, file_path)
            all_required_section_found = False

    return all_required_section_found


def check_naif_id_associations(data_text, sections_map, kernel_path):
    # Check NAIF IDs if any is found
    valid_ids = True

    try:
        naif_ids = get_naif_ids_from_text(data_text)
        FOUND_NAIF_IDS.extend(naif_ids)
    except Exception as ex:
        log_error("NAIF_IDS",
                  "Error while obtaining NAIF IDs from: " + kernel_path + " , exception: " + str(ex), kernel_path)
        return False

    if len(naif_ids):

        naif_id_section_patterns = ["@EW@NAIF ID Codes",
                                    "@EW@NAIF ID Codes to Name Mapping",
                                    "@EW@NAIF ID Codes -- Definitions"]
        naif_id_sections = get_matched_sections(sections_map, naif_id_section_patterns)

        # TODO: Remove this check when next TODO is implemented, for the moment just look for name and syno
        for naif_id in naif_ids.keys():
            for naif_id_section in naif_id_sections:
                # Note that synonyms array also contains the body_name
                if not (check_naif_id_in_section_text(naif_id, naif_ids[naif_id]["synonyms"],
                                                      naif_id_section[0], naif_id_section[1], kernel_path)):
                    valid_ids = False

    """
    # TODO: Continue implementation of commented code, it parses the NAIF Ids from the description tables
    #       and checks that are consistent with naif id code associations. 
    #       For the moment is not working because the are still work in progress for function: 
    #           files.get_naif_ids_from_text_with_tables()

    naif_ids_table1 = get_naif_ids_from_text_with_tables(naif_id_codes_sec_text)
    naif_ids_table2 = get_naif_ids_from_text_with_tables(naif_id_codes_map_sec_text)

    naif_ids_set = set(naif_ids.keys())
    naif_ids_table1_set = set(naif_ids_table1.keys())
    naif_ids_table2_set = set(naif_ids_table2.keys())

    if naif_ids_set != naif_ids_table1_set or naif_ids_set != naif_ids_table2_set:

        all_naif_ids = naif_ids_set.union(naif_ids_table1_set).union(naif_ids_table2_set)

        for naif_id in all_naif_ids:

            valid_id = True

            if naif_id not in naif_ids:
                print("ERROR: NAIF ID Code: " + str(naif_id) + " not found in NAIF_BODY_CODEs at " + fk_path)
                valid_id = False

            if naif_id not in naif_ids_table1:
                print("ERROR: NAIF ID Code: " + str(naif_id) + " not found in section " + 
                        "'NAIF ID Codes' section at " + fk_path)
                valid_id = False

            if naif_id not in naif_ids_table2:
                print("ERROR: NAIF ID Code: " + str(naif_id) + " not found in section " + 
                        "'NAIF ID Codes to Name Mapping' section at " + fk_path)
                valid_id = False

            if valid_id:

                set1 = set(naif_ids[naif_id]["synonyms"])
                set2 = set(naif_ids_table1[naif_id]["synonyms"])
                set3 = set(naif_ids_table2[naif_id]["synonyms"])

                all_synonyms = set1.union(set2).union(set3)
                for synonym in all_synonyms:

                    if synonym not in naif_ids[naif_id]["synonyms"]:
                        print("ERROR: NAIF BODY Name: " + str(synonym) + " not found in NAIF_BODY_CODEs "
                                                                         "for NAIF Id: " + str(
                            naif_id) + " at " + fk_path)
                        valid_id = False

                    if synonym not in naif_ids_table1[naif_id]["synonyms"]:
                        print("ERROR: NAIF BODY Name: " + str(synonym) + " not found in 'NAIF ID Codes' section "
                                                                         "for NAIF Id: " + str(
                            naif_id) + " at " + fk_path)
                        valid_id = False

                    if synonym not in naif_ids_table2[naif_id]["synonyms"]:
                        print("ERROR: NAIF BODY Name: " + str(
                            synonym) + " not found in 'NAIF ID Codes to Name Mapping' section "
                                       "for NAIF Id: " + str(naif_id) + " at " + fk_path)
                        valid_id = False

            valid_ids = valid_ids and valid_id
    """

    return valid_ids


def check_naif_id_in_section_text(naif_id, synonyms, section_name, section_text, kernel_path):

    naif_id_is_valid = True

    if str(naif_id) not in section_text:

        # Check if we shall look for naif_id ended in NN like: -12151NN*
        if len(synonyms) == 1:
            last_name_part = synonyms[0].split("_")[-1]
            if is_number(last_name_part):
                n_digits = len(last_name_part)
                generic_naif_id = str(naif_id)[0:-n_digits] + "N" * len(last_name_part)
                generic_synonym = synonyms[0][0:-n_digits] + "N" * len(last_name_part)
                return check_naif_id_in_section_text(generic_naif_id, [generic_synonym],
                                                     section_name, section_text, kernel_path)

        log_error("NAIF_IDS",
                  "NAIF ID Code: " + str(naif_id) + " not found at section: '" + section_name, kernel_path)
        naif_id_is_valid = False

    for synomyn in synonyms:
        if synomyn not in section_text:
            # We need to check that the synonym has not been chunked in two lines because it has a long name
            if synomyn not in " ".join(section_text.replace("\n", " ").split()):
                log_error("NAIF_IDS",
                          "NAIF BODY Name: " + str(synomyn) + " not found at section: '" + section_name, kernel_path)
                naif_id_is_valid = False

    return naif_id_is_valid


def check_frame_definitions(data_text, sections_map, fk_path):
    try:
        frames = get_frames_definitions_from_text(data_text)

        for frame_id in frames:
            FOUND_FRAME_IDS.append(frame_id)
            if "frame_name" in frames[frame_id]:
                FOUND_FRAME_NAMES.append(frames[frame_id]["frame_name"])

    except Exception as ex:
        log_error("WRONG_DEFINITIONS",
                  "Error while obtaining frame definitions from: " + fk_path + " , exception: " + str(ex), fk_path)
        return False

    not_found_ids = []
    frames_are_valid = True
    if len(frames):

        frames_section_patterns = ["@EW@Mission Frames"]
        # TODO: Include specific frame definition sections to frames_section_patterns,
        #       eg: "JUICE Medium Gain Antenna Frames" ...

        frame_sections = get_matched_sections(sections_map, frames_section_patterns)

        # Check that frame Ids and Frame names are in the comments sections
        for frame_id in frames.keys():
            for frame_section in frame_sections:

                if str(frame_id) not in frame_section[1]:
                    log_error("MISALIGNED_SECTION",
                              "FRAME ID Code: " + str(frame_id) + " not found at section: '" + frame_section[0]
                              + "' at " + fk_path, fk_path)
                    frames_are_valid = False
                    not_found_ids.append(frame_id)

                if "frame_name" in frames[frame_id]:
                    frame_name = frames[frame_id]["frame_name"]
                    if frame_name not in frame_section[1]:
                        log_error("MISALIGNED_SECTION",
                                  "FRAME NAME: " + frame_name + " not found at section: '" + frame_section[0]
                                  + "' at " + fk_path, fk_path)
                        frames_are_valid = False

        # Validate each frame definition
        keyword_indent = None  # Must be the same for all frames

        for frame_id in frames:

            if frame_id in not_found_ids:
                # Skip because we already know that its definition is wrong:
                continue

            keyword_indent = check_keywords_indentation(frames[frame_id]["keywords"], keyword_indent, fk_path)

            frames_is_valid = check_kernel_keywords(frames[frame_id], "frame_class_Any",
                                                    FRAME_DEFINITION_KEYWORDS, fk_path)
            if not frames_is_valid:
                frames_are_valid = False

    return frames_are_valid


def check_keywords_indentation(keywords, keyword_indent, path):

    equal_indent = None  # Must be the same inside each frame
    value_indent = None  # Must be the same inside each frame

    for keyword_key in keywords:
        keyword_data = keywords[keyword_key]

        # Check indentation
        if equal_indent is None \
                or ("indent_break" in keyword_data and keyword_data["indent_break"]):
            equal_indent = keyword_data["equal_indent"]

            value_indent = keyword_data["value_indent"]
            if is_number(keyword_data["value"]) and float(keyword_data["value"]) >= 0.0:
                # In case of first value is a positive number, is shall have an extra blank
                # so our indentation is one char minus
                value_indent = value_indent - 1

            if keyword_indent is None:
                keyword_indent = keyword_data["keyword_indent"]
        else:

            tmp_value_indent = keyword_data["value_indent"]
            if is_number(keyword_data["value"]) and float(keyword_data["value"]) >= 0.0:
                # In case of value where is a positive number, is shall have an extra blank
                # so our indentation is one char minus
                tmp_value_indent = tmp_value_indent - 1

            if keyword_data["keyword_indent"] != keyword_indent:
                log_warn("WRONG_INDENTATION",
                          "WRONG INDENTATION OF KEYWORD: '" + keyword_data["var"] + "' at line: '" +
                          keyword_data["line"] + "' at " + path, path)
            elif keyword_data["equal_indent"] != equal_indent:
                log_warn("WRONG_INDENTATION",
                         "WRONG INDENTATION OF '=' at line: '" + keyword_data["line"] + "' at " + path, path)
            elif tmp_value_indent != value_indent:
                log_warn("WRONG_INDENTATION",
                         "WRONG INDENTATION OF '" + keyword_data["value"] + "' at line: '" +
                         keyword_data["line"] + "' at " + path, path)

    return keyword_indent


def check_kernel_keywords(def_obj, keywords_ref_key, keywords_ref_map, path):
    keywords_valid = True

    keywords_ref = keywords_ref_map[keywords_ref_key]

    keywords = def_obj["keywords"]
    for keyword_ref_data in keywords_ref:

        keyword_ref = keyword_ref_data["keyword"]
        if keyword_ref not in keywords:

            if "optional" in keyword_ref_data:
                if eval(keyword_ref_data["optional"]):
                    continue  # Ignore this keyword in this case

            log_error("WRONG_KEYWORD",
                      "MISSING KEYWORD AT DEFINITION: " + keyword_ref + " not found at: \n" + def_obj["definition"],
                      path)
            keywords_valid = False
            continue

        keyword_data = keywords[keyword_ref]

        # Check keyword validity
        var_ref = replace_tokens(keyword_ref_data["keyword"], keyword_data, def_obj)
        if keyword_data["var"] != var_ref:
            log_error("WRONG_KEYWORD",
                      "WRONG KEYWORD AT DEFINITION: " + keyword_data["var"] + " expected: '" + var_ref, path)
            keywords_valid = False

        # Check line order
        if "line_nr" in keyword_ref_data:
            if keyword_data["line_nr"] != keyword_ref_data["line_nr"]:
                log_warn("WRONG_KEYWORD_ORDER",
                          "WRONG LINE ORDER FOR KEYWORD '" + keyword_data["var"] + "' " +
                          "found at line nr: " + str(keyword_data["line_nr"]) +
                          " expected at line nr: " + str(keyword_ref_data["line_nr"]), path)

        # Check proper value
        value = ""
        if "value" in keyword_ref_data:

            value_ref = keyword_ref_data["value"]
            value = keyword_data["value"]  # To have value variable inside eval context
            if isinstance(value, str):
                # Check number of "'" in string
                if "'" in value and len(value.split("'")) % 2 != 1:
                    log_error("WRONG_KEYWORD", "WRONG NUMBER OF \"'\" FOUND AT LINE: '" + keyword_data["line"], path)
                    keywords_valid = False

                # Remove "'" from sting
                value = value.replace("'", "")

            if "{" in value_ref and not value_ref.startswith("="):
                value_ref = replace_tokens(value_ref, keyword_data, def_obj)
                if value != value_ref:
                    log_error("WRONG_KEYWORD",
                              "WRONG VALUE FOUND AT LINE: '" + keyword_data["line"] + "' " +
                              "found: '" + str(value) + "' expected: '" + str(value_ref), path)
                    keywords_valid = False

            elif value_ref.startswith("["):
                value_ref = eval(value_ref)
                if value not in value_ref:
                    log_error("WRONG_KEYWORD",
                              "WRONG VALUE FOUND AT LINE: '" + keyword_data["line"] + "' " +
                              "found: '" + str(value) + "' expected: '" + str(value_ref), path)
                    keywords_valid = False

            elif value_ref.startswith("="):

                result = eval(replace_tokens(value_ref[1:], keyword_data, def_obj))

                reason = None
                if isinstance(result, tuple):
                    valid_value = result[0]
                    reason = result[1]
                else:
                    valid_value = result

                if not valid_value:

                    reason_text = ""
                    if reason is not None:
                        reason_text = ", reason: " + reason + " "

                    log_error("WRONG_KEYWORD",
                              "WRONG VALUE FOUND AT LINE: '" + keyword_data["line"] + "' " + reason_text +
                              "found: '" + str(value) + "' expected: '" + str(value_ref), path)
                    keywords_valid = False

            elif value_ref == "NAIF_ID":

                if not is_naif_id(value):
                    log_warn("WRONG_KEYWORD",
                              "WARNING: WRONG VALUE FOUND AT LINE: '" + keyword_data["line"] + "' " +
                              "found: '" + str(value) + "' expected any of defined NAIF IDs " +
                              "at the validated kernels or any of the SPICE BUILT-IN BODY IDs.\n" +
                              "Check if this BODY ID has been defined in other kernel.\n" +
                              "Warning raised at " + path, path)

            elif value_ref == "FRAME_NAME" \
                    or value_ref == "FRAME_NAME_LIST":

                frame_names = []
                if value_ref == "FRAME_NAME_LIST":
                    if not is_spice_vector(value, str, check_duplicates=True):
                        log_error("WRONG_KEYWORD",
                                  "WRONG FRAME NAME LIST FOUND AT LINE: '" + keyword_data["line"] + "' " +
                                  "found: '" + str(value), path)
                        keywords_valid = False
                    else:
                        frame_names.extend(spice_vector_to_tuple(value, str))
                else:
                    frame_names.append(value)

                for frm_name in frame_names:
                    if not is_frame_name(frm_name):
                        log_warn("WRONG_KEYWORD",
                                  "WARNING: WRONG FRAME NAME FOUND AT LINE: '" + keyword_data["line"] + "' " +
                                  "found: '" + str(frm_name) + "' expected any of defined FRAME NAMES " +
                                  "at the validated FKs or any of the SPICE BUILT-IN FRAMES.\n" +
                                  "Check if this FRAME NAME has been defined in other kernel.\n" +
                                  "Warning raised at " + path, path)

            else:
                raise NotImplementedError("Reference value not supported: " + value_ref)

        # Iterate over sub keyword in case of defined
        if "sub_keywords_key" in keyword_ref_data:

            sub_keywords_key = eval(keyword_ref_data["sub_keywords_key"][1:])
            if sub_keywords_key in keywords_ref_map:
                sub_keywords_valid = check_kernel_keywords(def_obj, sub_keywords_key, keywords_ref_map, path)
                if not sub_keywords_valid:
                    keywords_valid = False

            else:
                log_warn("WRONG_KEYWORD",
                         "WARNING: Could not check sub_keywords for key: " + sub_keywords_key
                         + ", Warning raised at " + path, path)

    return keywords_valid


def replace_tokens(text, keyword_data, spice_obj):

    for token in REPLACE_TOKENS:
        token_s = "{" + token + "}"
        if token_s in text:
            token_v = str(spice_obj[token]) \
                if token in spice_obj \
                else str(keyword_data[token])
            text = text.replace(token_s, token_v)
            if "{" not in text:
                break

    return text


def is_naif_id(naif_id):
    try:
        if not isinstance(naif_id, int):
            naif_id = int(naif_id)
    except:
        return False

    if naif_id not in FOUND_NAIF_IDS:
        try:
            # TODO: Load MK to have all defined NAIF IDs in the pool
            name = spiceypy.bodc2n(naif_id)
        except NotFoundError:
            return False

    return True


def is_frame_id(frame_id):
    try:
        if not isinstance(frame_id, int):
            frame_id = int(frame_id)
    except:
        return False

    if frame_id not in FOUND_FRAME_IDS:
        try:
            # TODO: Load MK to have all defined FRAME IDS in the pool
            frame_name = spiceypy.frmnam(frame_id)
        except NotFoundError:
            return False

    return True


def is_frame_name(frame_name):
    if not isinstance(frame_name, str):
        return False

    if frame_name not in FOUND_FRAME_NAMES:
        try:
            # TODO: Load MK to have all defined FRAME NAMES in the pool
            frame_id = spiceypy.namfrm(frame_name)
        except NotFoundError:
            return False

    return True


def spice_vector_to_tuple(text, elem_type):
    if "(" not in text or ")" not in text:
        raise Exception("Missing parenthesis")

    if "," not in text:
        # Eg: ( 1.0 4.0 5.0 )
        elems = text.replace("(", "").replace(")", "").split()
        new_elems = ["'" + elem + "'"
                     if not is_number(elem) and "'" not in elem
                     else elem
                     for elem in elems]

        text = "(" + ",".join(new_elems) + ")"

    elif "\n" in text:
        # Add "," to the line endings if not present. Eg: 0.00000,  1.00000,  0.00000
        new_text = ""
        comma_endings = None
        lines = text.splitlines()
        num_lines = len(lines)
        for line_idx in range(num_lines):
            line = lines[line_idx]
            if line_idx < num_lines - 1 \
                    and line.strip() != "(":
                next_line = lines[line_idx + 1]
                tmp_comma_endings = line.rstrip().endswith(",")
                if comma_endings is None:
                    comma_endings = tmp_comma_endings
                elif comma_endings != tmp_comma_endings and next_line.strip() != ")":
                    raise Exception("Different line endings with or without ','")

                new_text += line + ("," if not tmp_comma_endings
                                           and not line.rstrip().endswith(")")
                                           and next_line.strip() != ")"
                                    else "")
            else:
                new_text += line

        text = new_text

    if elem_type == "date_str":
        dates_texts = text.replace("(", "").replace(")", "").split(",")
        dates = []
        for date in dates_texts:
            dates.append(date.strip().replace("@", "'@") + "'")
        text = "(" + ",".join(dates) + ")"

    matrix = eval(text)
    if "," in text:
        if not isinstance(matrix, tuple):  # Eg: (0.0, 1.0, 2.0)
            raise Exception("Wrong (f0, ..) format")
    else:
        if not has_valid_type(matrix, elem_type):  # Eg: (0.0)
            raise Exception("Wrong (f0) format")
        else:
            matrix = [matrix]

    return matrix


def is_spice_vector(text, elem_type, size=None, values_range=None, check_duplicates=False):
    try:
        matrix = spice_vector_to_tuple(text, elem_type)

        if size is not None:
            if isinstance(size, int):
                if len(matrix) != size:
                    return False, "Wrong length or missing comma, expected " + str(size) + " elements."
            elif isinstance(size, str):
                if not eval(size):
                    return False, "Wrong size or missing comma."
            else:
                raise NotImplementedError("Unsupported size type at is_spice_vector, type: " + str(type(size)))

        for elem in matrix:
            if not has_valid_type(elem, elem_type):
                return False, "Wrong type for element: " + str(elem) + ", expected any of " + \
                              str(elem_type) + " types."

            if values_range is not None:
                if elem not in values_range:
                    return False, "Wrong value for element: " + str(elem) + ", expected any of " + \
                              str(values_range) + " range."

        if check_duplicates:
            if len(matrix) != len(set(matrix)):
                return False, "Duplicated values"

    except Exception as ex:
        return False, str(ex)

    return True


def has_valid_type(elem, elem_type):
    if elem_type == "date_str":
        elem_type = str

    elem_types = [elem_type]
    if isinstance(elem_type, list):
        elem_types = elem_type

    valid_type = False
    for e_type in elem_types:
        if isinstance(elem, e_type):
            valid_type = True
            break
    return valid_type


def is_number(value_s):
    try:
        val = float(value_s)
        return True
    except:
        return False


def check_instruments_definitions(data_text, sections_map, ik_path):
    try:
        instruments = get_instruments_definitions_from_text(data_text)
    except Exception as ex:
        log_error("WRONG_DEFINITIONS",
                  "Obtaining instruments definitions from: " + ik_path + " , exception: " + str(ex), ik_path)
        return False

    ins_are_valid = True
    if len(instruments):

        ins_section_patterns = ["@IN@Naming Conventions"]
        ins_sections = get_matched_sections(sections_map, ins_section_patterns)

        # Check that instrument Ids and name are in the comments sections
        for ins_id in instruments:
            for section in ins_sections:

                if str(ins_id) not in section[1]:
                    log_error("MISALIGNED_SECTION",
                              "INSTRUMENT ID Code: " + str(ins_id) + " not found at section: '" + section[0], ik_path)
                    ins_are_valid = False

                if "name" in instruments[ins_id]:
                    ins_name = instruments[ins_id]["name"]
                    if ins_name not in section[1]:
                        log_error("MISALIGNED_SECTION",
                                  "INSTRUMENT NAME: " + ins_name + " not found at section: '" + section[0], ik_path)
                        ins_are_valid = False

        # Validate each instrument definition
        keyword_indent = None  # Must be the same for all instruments

        for ins_id in instruments:

            keyword_indent = check_keywords_indentation(instruments[ins_id]["keywords"], keyword_indent, ik_path)

            ins_is_valid = check_kernel_keywords(instruments[ins_id], "instrument_Any",
                                                 INSTRUMENT_DEFINITION_KEYWORDS, ik_path)

            if not ins_is_valid:
                ins_are_valid = False

    return ins_are_valid


def check_sites_definitions(data_text, sections_map, spk_path):
    try:
        sites = get_sites_definitions_from_text(data_text)
    except Exception as ex:
        log_error("WRONG_DEFINITIONS",
                  "Obtaining sites definitions from: " + spk_path + " , exception: " + str(ex), spk_path)
        return False

    sites_are_valid = True
    if len(sites):

        sites_section_patterns = ["Structure location specification -- Definitions",
                                  "Coordinates"]
        sites_sections = get_matched_sections(sections_map, sites_section_patterns)

        # Check that site Ids and site names are in the comments sections
        for site_name in sites.keys():

            id_code = None
            if "{name}_IDCODE" in sites[site_name]["keywords"]:
                id_code = sites[site_name]["keywords"]["{name}_IDCODE"]["value"]
                if is_number(id_code) and id_code not in FOUND_NAIF_IDS:
                    FOUND_NAIF_IDS.append(int(id_code))

            for section in sites_sections:

                if section[0] != "Coordinates":
                    if site_name not in section[1]:
                        log_error("MISALIGNED_SECTION",
                                  "SITE Name: '" + site_name + "' not found at section: '" + section[0], spk_path)
                        sites_are_valid = False

                if id_code is not None:
                    if str(id_code) not in section[1]:
                        log_error("MISALIGNED_SECTION",
                                  "SITE IDCODE: " + str(id_code) + " not found at section: '" + section[0], spk_path)
                        sites_are_valid = False

                if "{name}_FRAME" in sites[site_name]["keywords"]:
                    frmae_name = sites[site_name]["keywords"]["{name}_FRAME"]["value"].replace("'", "")
                    if frmae_name not in section[1]:
                        log_error("MISALIGNED_SECTION",
                                  "SITE FRAME: '" + frmae_name + "' not found at section: '" + section[0], spk_path)
                        sites_are_valid = False

                if section[0] == "Coordinates":
                    if "{name}_CENTER" in sites[site_name]["keywords"]:
                        center = sites[site_name]["keywords"]["{name}_CENTER"]["value"]
                        if str(center) not in section[1]:
                            log_error("MISALIGNED_SECTION",
                                      "SITE CENTER: " + str(center) + " not found at section: '" + section[0], spk_path)
                            sites_are_valid = False

        # Validate each site definition
        keyword_indent = None  # Must be the same for all instruments

        for site_name in sites:

            keyword_indent = check_keywords_indentation(sites[site_name]["keywords"], keyword_indent, spk_path)

            site_is_valid = check_kernel_keywords(sites[site_name], "sites_Any",
                                                  PINPOINT_DEFINITION_KEYWORDS, spk_path)

            if not site_is_valid:
                sites_are_valid = False

    return sites_are_valid


def get_matched_sections(sections_map, section_patterns):
    sections = []
    for sec_pattern in section_patterns:
        sec_name, sec_text = get_section_from_sections_map(sec_pattern, sections_map)
        if sec_name is not None:
            sections.append([sec_name, sec_text])
    return sections
