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
    validate_trailing_chars, read_all_text, get_data_text_from_text_kernel, get_sections_map_from_kernel_comments, \
    get_section_from_sections_map, get_naif_ids_from_text, \
    get_frames_definitions_from_text


# Modification of:
# https://spiceypy.readthedocs.io/en/main/other_stuff.html#lesson-1-kernel-management-with-the-kernel-subsystem


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
                print("ERROR!! - NOT A VALID TEXT KERNEL: " + kernel_file)
                is_valid = False

        else:
            # Is a binary kernel file, extract comments:
            if not is_valid_binary_kernel(kernel_file,
                                          check_line_length, check_indentation, check_trailing_chars):
                print("ERROR!! - NOT A VALID BINARY KERNEL: " + kernel_file)
                is_valid = False

        if is_mk_file(kernel_file):
            if not is_valid_metakernel(kernel_file):
                print("ERROR!! - WRONG META-KERNEL: " + kernel_file)
                is_valid = False

    else:
        print("ERROR!! - NOT A KERNEL EXTENSION: " + extension + " for file " + kernel_file)
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
        if not is_valid_frameskernel(filename):
            print("ERROR!! - WRONG FRAMES-KERNEL: " + filename)
            is_valid = False

    # TODO: Continue implementation

    return is_valid


def is_valid_comment_file(filename, check_line_length=True, check_indentation=True, check_trailing_chars=True):

    if is_empty_file(filename):
        print("ERROR!! - EMPTY FILE: " + filename)
        return False

    is_valid = True
    if has_badchars(filename):
        print("ERROR!! - HAS BAD CHARS: " + filename)
        is_valid = False

    if check_line_length:
        if exceeds_line_lengths(filename, ignore_lines=COMMENTS_FILE_IGNORE_LINES):
            print("ERROR!! - EXCEEDS LINE LENGTH: " + filename)
            is_valid = False

    if check_indentation:
        if validate_indentation(filename, indentation=3):
            print("ERROR!! - HAS WRONG INDENTATION: " + filename)
            is_valid = False

    if check_trailing_chars:
        if validate_trailing_chars(filename):
            print("ERROR!! - HAS TRAILING CHARS: " + filename)
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
    if not is_valid:
        print("ERROR!! - WRONG COMMENTS: " + filename)
    os.remove(comment_filename)

    if not has_valid_version_and_date_section(filename):
        is_valid = False

    if not has_valid_contact_section(filename):
        is_valid = False

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
                    if is_versioned_mk(mk_filename):
                        if not filename.endswith(str(cvars[0])):
                            print("ERROR: Variable SKD_VERSION: " + str(cvars[0]) +
                                  " doesn't match MK filename: " + mk_filename)
                            is_valid_mk = False
                    else:
                        # Check that an MK with name MK_IDENTIFIER exists in the MKs path
                        related_mk = filename + "_" + str(cvars[0]) + extension
                        if not os.path.exists(related_mk):
                            print("ERROR: No MK ( " + related_mk + " ) with version found for "
                                  "SKD_VERSION: " + str(cvars[0]) + " at MK filename: " + mk_filename)
                            is_valid_mk = False

                elif cval == "MK_IDENTIFIER":
                    if is_versioned_mk(mk_filename):
                        # Check filename aligned with MK_IDENTIFIER for MKs with version
                        if str(cvars[0]) != filename:
                            print("ERROR: Variable MK_IDENTIFIER: " + str(cvars[0]) +
                                  " doesn't match MK filename: " + mk_filename)
                            is_valid_mk = False
                    else:
                        # Check that an MK with name MK_IDENTIFIER exists in the MKs path
                        related_mk = str(cvars[0]) + extension
                        if not os.path.exists(related_mk):
                            print("ERROR: No MK ( " + related_mk + " ) with version found for "
                                  "MK_IDENTIFIER: " + str(cvars[0]) + " at MK filename: " + mk_filename)
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

    if extension == ".tsc":
        if "_v" not in os.path.basename(kernel_file).lower():
            # Ignore this check for SCLK Kernels with no version in the filename, such as: integral_fict_20220208.tsc
            return True

    text = get_section_text_from_kernel_comments(kernel_file, "Version and Date")
    if not len(text):
        if mandatory:
            print("ERROR: No 'Version and Date' section found in kernel: " + kernel_file)
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
        print("ERROR: Could not obtain kernel version from kernel: " + kernel_file + " , ex: " + str(ex))
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
                    print("ERROR: Version in 'Version and Date' section is greater than expected "
                          "in kernel: " + kernel_file + " with version: " + str(kernel_version) + ", at line: " + line)
                    return False

                if version < tmp_kernel_version:
                    print("ERROR: Version in 'Version and Date' section is smaller than expected "
                          "in kernel: " + kernel_file + " with version: " + str(kernel_version) + ", at line: " + line)
                    return False

                tmp_kernel_version = tmp_kernel_version - multiplier

            except Exception as ex:
                print("ERROR: Wrong version text format in 'Version and Date' section found in kernel: "
                      + kernel_file + " with version: " + str(kernel_version) + ", at line: " + line)
                return False

    if tmp_kernel_version > -1:
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


def get_skd_version(skd_path):

    version_file = os.path.join(skd_path, "version")
    if not os.path.exists(version_file):
        raise Exception("Version file not found at path: " + version_file)

    version = read_all_text(version_file).strip()
    if len(version) != 4 or not version.startswith("v"):
        raise Exception("Wrong formatted version: '" + version + "' found at: " + version_file)

    return version


def is_mk_file(mk_path):
    mk_filename = os.path.basename(mk_path)
    return str(os.path.splitext(mk_filename)[1]).lower() == ".tm"


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
            print("ERROR: No 'Release History' section found in kernel: " + rel_notes_file)
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
            print("ERROR: Filename versions: " + rel_notes_file + " doesn't match the version: " + version
                  + " at line: " + first_line)
            is_valid = False

    # First paragraph shall contain "(version)"
    ver_text = "(" + version.replace("v", "") + ")"
    if ver_text not in text:
        print("ERROR: Text : " + ver_text + " not found in first paragraph of: " + rel_notes_file)
        is_valid = False

    notes = get_section_text_from_kernel_comments(rel_notes_file, "Notes")
    if not len(notes):
        print("ERROR: No 'Notes' section found in kernel: " + rel_notes_file)

    elif version not in notes:
        print("ERROR: Version : " + version + " not found in Notes section of: " + rel_notes_file)
        is_valid = False

    return is_valid


def is_fk_file(fk_path):
    fk_filename = os.path.basename(fk_path)
    return str(os.path.splitext(fk_filename)[1]).lower() == ".tf"


def is_valid_frameskernel(fk_path):

    try:
        data_text, comments = get_data_text_from_text_kernel(fk_path)
    except Exception as ex:
        print("ERROR!! - Obtaining data text from: " + fk_path + " , exception: " + str(ex))
        return False

    if not len(data_text):
        print("ERROR: No data sections found in kernel: " + fk_path)
        return False

    if not len(comments):
        print("ERROR: No text comments found in kernel: " + fk_path)
        return False

    # Don't continue if is a PINPOINT FK
    if "This file was created by PINPOINT." in comments:
        print("Info: Not all FK checks were performed because is a PINPOINT FK: " + fk_path)
        return True

    sections_map = get_sections_map_from_kernel_comments(comments)
    if sections_map is None:
        print("ERROR: Could not obtain sections from kernel: " + fk_path)
        return False

    # Check required sections
    all_required_section_found = check_required_sections(sections_map, REQUIRED_SECTIONS["FK"], fk_path)

    # Check NAIF IDs if any is found
    valid_ids = check_naif_id_associations(data_text, sections_map, fk_path)

    # Check frames definitions
    valid_frames = check_frame_definitions(data_text, sections_map, fk_path)

    return all_required_section_found and valid_ids and valid_frames


def check_required_sections(sections_map, required_sections, file_path):
    all_required_section_found = True

    for section_name in required_sections:
        sec_name, sec_text = get_section_from_sections_map(section_name, sections_map)

        if sec_name is None:
            print("ERROR: Required section not found: '" + section_name + "' at " + file_path)
            all_required_section_found = False

        if not len(str(sec_text).strip()):
            print("ERROR: Required section is empty: '" + section_name + "' at " + file_path)
            all_required_section_found = False

    return all_required_section_found


def check_naif_id_associations(data_text, sections_map, fk_path):
    # Check NAIF IDs if any is found
    valid_ids = True

    try:
        naif_ids = get_naif_ids_from_text(data_text)
        FOUND_NAIF_IDS.extend(naif_ids)
    except Exception as ex:
        print("ERROR!! - Obtaining NAIF IDs from: " + fk_path + " , exception: " + str(ex))
        return False

    if len(naif_ids):

        naif_id_section_patters = ["@EW@NAIF ID Codes",
                                   "@EW@NAIF ID Codes to Name Mapping",
                                   "@EW@NAIF ID Codes -- Definitions"]
        naif_id_sections = []
        for sec_pattern in naif_id_section_patters:
            sec_name, sec_text = get_section_from_sections_map(sec_pattern, sections_map)
            if sec_name is not None:
                naif_id_sections.append([sec_name, sec_text])

        # TODO: Remove this check when next TODO is implemented, for the moment just look for name and syno
        for naif_id in naif_ids.keys():
            for naif_id_section in naif_id_sections:
                # Note that synonyms array also contains the body_name
                if not (check_naif_id_in_section_text(naif_id, naif_ids[naif_id]["synonyms"],
                                                      naif_id_section[0], naif_id_section[1], fk_path)):
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


def check_naif_id_in_section_text(naif_id, synonyms, section_name, section_text, fk_path):

    naif_id_is_valid = True

    if str(naif_id) not in section_text:
        print("ERROR: NAIF ID Code: " + str(naif_id) +
              " not found at section: '" + section_name + "' at " + fk_path)
        naif_id_is_valid = False

    for synomyn in synonyms:
        if synomyn not in section_text:
            # We need to check that the synonym has not been chunked in two lines because it has a long name
            if synomyn not in " ".join(section_text.replace("\n", " ").split()):
                print("ERROR: NAIF BODY Name: " + str(synomyn) +
                      " not found at section: '" + section_name + "' at " + fk_path)
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
        print("ERROR!! - Obtaining frame definitions from: " + fk_path + " , exception: " + str(ex))
        return False

    not_found_ids = []
    frames_are_valid = True
    if len(frames):

        frames_section_patters = ["@EW@Mission Frames"]
        # TODO: Include specific frame definition sections to frames_section_patters,
        #       eg: "JUICE Medium Gain Antenna Frames" ...

        frame_sections = []
        for sec_pattern in frames_section_patters:
            sec_name, sec_text = get_section_from_sections_map(sec_pattern, sections_map)
            if sec_name is not None:
                frame_sections.append([sec_name, sec_text])

        # Check that frame Ids and Frame names are in the comments sections
        for frame_id in frames.keys():
            for frame_section in frame_sections:

                if str(frame_id) not in frame_section[1]:
                    print("ERROR: FRAME ID Code: " + str(frame_id) +
                          " not found at section: '" + frame_section[0] + "' at " + fk_path)
                    frames_are_valid = False
                    not_found_ids.append(frame_id)

                if "frame_name" in frames[frame_id]:
                    frame_name = frames[frame_id]["frame_name"]
                    if frame_name not in frame_section[1]:
                        print("ERROR: FRAME NAME: " + frame_name +
                              " not found at section: '" + frame_section[0] + "' at " + fk_path)
                        frames_are_valid = False

        # Validate each frame definition
        keyword_indent = None  # Must be the same for all frames

        for frame_id in frames:

            if frame_id in not_found_ids:
                # Skip because we already know that its definition is wrong:
                continue

            equal_indent = None  # Must be the same inside each frame
            value_indent = None  # Must be the same inside each frame

            keywords_ref = FRAME_DEFINITION_KEYWORDS["frame_class_Any"]

            frames_is_valid, keyword_indent, equal_indent, value_indent = check_frame_keywords(frames[frame_id],
                                                                                               keywords_ref, fk_path,
                                                                                               keyword_indent,
                                                                                               equal_indent,
                                                                                               value_indent)
            if not frames_is_valid:
                frames_are_valid = False

    return frames_are_valid


def check_frame_keywords(frame_obj, keywords_ref, fk_path, keyword_indent, equal_indent, value_indent):
    frame_if_valid = True

    frame_class = None  # To have frame_class variable inside eval context
    if "frame_class" in frame_obj:
        frame_class = frame_obj["frame_class"]

    keywords = frame_obj["keywords"]
    for keyword_ref_data in keywords_ref:

        keyword_ref = keyword_ref_data["keyword"]
        if keyword_ref not in keywords:
            print("ERROR: MISSING KEYWORD AT FRAME DEFINITION: " + keyword_ref +
                  " not found at: \n" + frame_obj["frame_definition"] + "\n at " + fk_path)
            frame_if_valid = False
            continue

        keyword_data = keywords[keyword_ref]

        # Check keyword validity
        var_ref = replace_tokens(keyword_ref_data["keyword"], frame_obj, keyword_data)
        if keyword_data["var"] != var_ref:
            print("ERROR: WRONG KEYWORD AT FRAME DEFINITION: " + keyword_data["var"] +
                  " expected: '" + var_ref + "' at " + fk_path)
            frame_if_valid = False

        # Check indentation
        if equal_indent is None:
            equal_indent = keyword_data["equal_indent"]
            value_indent = keyword_data["value_indent"]
            if keyword_indent is None:
                keyword_indent = keyword_data["keyword_indent"]
        else:
            if keyword_data["keyword_indent"] != keyword_indent:
                print("WARNING: WRONG INDENTATION OF KEYWORD: '" + keyword_data["var"] + "' at line: '" +
                      keyword_data["line"] + "' at " + fk_path)
            elif keyword_data["equal_indent"] != equal_indent:
                print("WARNING: WRONG INDENTATION OF '=' at line: '" + keyword_data["line"] + "' at " + fk_path)
            elif keyword_data["value_indent"] != value_indent:
                print("WARNING: WRONG INDENTATION OF '" + keyword_data["value"] + "' at line: '" +
                      keyword_data["line"] + "' at " + fk_path)

        # Check line order
        if "line_nr" in keyword_ref_data:
            if keyword_data["line_nr"] != keyword_ref_data["line_nr"]:
                print("WARNING: WRONG LINE ORDER FOR KEYWORD '" + keyword_data["var"] + "' " +
                      "found at line nr: " + str(keyword_data["line_nr"]) +
                      " expected at line nr: " + str(keyword_ref_data["line_nr"]) + " at " + fk_path)

        # Check proper value
        value = ""
        if "value" in keyword_ref_data:

            value_ref = keyword_ref_data["value"]
            value = keyword_data["value"]  # To have value variable inside eval context
            if isinstance(value, str):
                # Check number of "'" in string
                if "'" in value and len(value.split("'")) % 2 != 1:
                    print("ERROR: WRONG NUMBER OF \"'\" FOUND AT LINE: '" + keyword_data["line"] + "' at " + fk_path)
                    frame_if_valid = False

                # Remove "'" from sting
                value = value.replace("'", "")

            if "{" in value_ref and not value_ref.startswith("="):
                value_ref = replace_tokens(value_ref, frame_obj, keyword_data)
                if value != value_ref:
                    print("ERROR: WRONG VALUE FOUND AT LINE: '" + keyword_data["line"] + "' " +
                          "found: '" + str(value) + "' expected: '" + str(value_ref)
                          + "' at " + fk_path)
                    frame_if_valid = False

            elif value_ref.startswith("["):
                value_ref = eval(value_ref)
                if value not in value_ref:
                    print("ERROR: WRONG VALUE FOUND AT LINE: '" + keyword_data["line"] + "' " +
                          "found: '" + str(value) + "' expected: '" + str(value_ref)
                          + "' at " + fk_path)
                    frame_if_valid = False

            elif value_ref.startswith("="):

                result = eval(replace_tokens(value_ref[1:], frame_obj, keyword_data))

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

                    print("ERROR: WRONG VALUE FOUND AT LINE: '" + keyword_data["line"] + "' " + reason_text +
                          "found: '" + str(value) + "' expected: '" + str(value_ref)
                          + "' at " + fk_path)
                    frame_if_valid = False

            elif value_ref == "NAIF_ID":

                if not is_naif_id(value):
                    print("WARNING: WRONG VALUE FOUND AT LINE: '" + keyword_data["line"] + "' " +
                          "found: '" + str(value) + "' expected any of defined NAIF IDs " +
                          "at the validated FKs or any of the SPICE BUILT-IN BODY IDs.\n" +
                          "Check if this BODY ID has been defined in other kernel.\n" +
                          "Warning raised at " + fk_path)

            elif value_ref == "FRAME_NAME" \
                    or var_ref == "FRAME_NAME_LIST":

                frame_names = []
                if var_ref == "FRAME_NAME_LIST":
                    if not is_spice_vector(value, str, check_duplicates=True):
                        print("ERROR: WRONG FRAME NAME LIST FOUND AT LINE: '" + keyword_data["line"] + "' " +
                              "found: '" + str(value) + "' at " + fk_path)
                        frame_if_valid = False
                    else:
                        frame_names.extend(eval(value))
                else:
                    frame_names.append(value)

                for frm_name in frame_names:
                    if not is_frame_name(frm_name):
                        print("WARNING: WRONG FRAME NAME FOUND AT LINE: '" + keyword_data["line"] + "' " +
                              "found: '" + str(frm_name) + "' expected any of defined FRAME NAMES " +
                              "at the validated FKs or any of the SPICE BUILT-IN FRAMES.\n" +
                              "Check if this FRAME NAME has been defined in other kernel.\n" +
                              "Warning raised at " + fk_path)

            else:
                raise NotImplementedError("Reference value not supported: " + value_ref)

        # Iterate over sub keyword in case of defined
        if "sub_keywords_key" in keyword_ref_data:

            sub_keywords_key = eval(keyword_ref_data["sub_keywords_key"][1:])
            if sub_keywords_key in FRAME_DEFINITION_KEYWORDS:
                keywords_ref = FRAME_DEFINITION_KEYWORDS[sub_keywords_key]

                sub_keywords_valid, keyword_indent, equal_indent, value_indent = check_frame_keywords(frame_obj,
                                                                                                      keywords_ref,
                                                                                                      fk_path,
                                                                                                      keyword_indent,
                                                                                                      equal_indent,
                                                                                                      value_indent)
                if not sub_keywords_valid:
                    frame_if_valid = False

            else:
                print("WARNING: Could not check sub_keywords for key: " + sub_keywords_key
                      + ", Warning raised at " + fk_path)

    return frame_if_valid, keyword_indent, equal_indent, value_indent


def replace_tokens(text, frame_obj, keyword_data):

    if "{frame_id}" in text:
        text = text.replace("{frame_id}", str(frame_obj["frame_id"]))

    if "{frame_name}" in text:
        text = text.replace("{frame_name}", frame_obj["frame_name"])

    if "{used_id}" in text:
        text = text.replace("{used_id}", str(keyword_data["used_id"]))

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


def is_spice_vector(text, elem_type, size=None, values_range=None, check_duplicates=False):
    try:
        if "(" not in text or ")" not in text:
            return False, "Missing parenthesis"

        if "," not in text:
            # Eg: ( 1.0 4.0 5.0 )
            text = "(" + ",".join(text.replace("(", "").replace(")", "").split()) + ")"

        matrix = eval(text)
        if not isinstance(matrix, tuple):
            return False, "Wrong format"

        if size is not None:
            if len(matrix) != size:
                return False, "Wrong length or missing comma, expected " + str(size) + " elements."

        elem_types = [elem_type]
        if isinstance(elem_type, list):
            elem_types = elem_type

        for elem in matrix:

            valid_type = False
            for e_type in elem_types:
                if isinstance(elem, e_type):
                    valid_type = True
                    break
            if not valid_type:
                return False, "Wrong type for element: " + str(elem) + ", expected any of " + \
                              str(elem_types) + " types."

            if values_range is not None:
                if elem not in values_range:
                    return False, "Wrong value for element: " + str(elem) + ", expected any of " + \
                              str(values_range) + " range."

        if check_duplicates:
            if len(matrix) != len(set(matrix)):
                return False, "Duplicated values"

    except:
        return False

    return True

