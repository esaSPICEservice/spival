import fnmatch
import glob
import os

from spival.utils.skd_constants import *
from spival.utils.files import exceeds_line_lengths, has_badchars, is_empty_file, files_are_equal, is_valid_pds_filename
from spival.utils.skd_utils import KERNEL_EXTENSIONS, is_valid_kernel, has_valid_contact_section, get_skd_version, \
    is_versioned_mk, get_versions_history_from_release_notes_file, check_release_notes_version
from spival.utils.skd_val_logger import log_error, log_info, write_file_report


def is_valid_doc_file(file_path):

    if is_empty_file(file_path):
        log_error("EMPTY_FILE", "File is empty", file_path)
        return False

    if has_badchars(file_path):
        log_error("HAS_BAD_CHARS", "Has bad chars.", file_path)
        return False

    basename = os.path.basename(file_path)
    filename, extension = os.path.splitext(basename)
    filename = str(filename).lower()
    extension = str(extension).lower()

    if CHECK_LINE_LENGTHS and extension not in LONG_LINE_EXTENSIONS:
        if exceeds_line_lengths(file_path):
            log_error("HAS_LONG_LINES", "Has long lines.=", file_path)
            return False

    if extension == ".txt":
        is_contact_section_mandatory = (filename == "aareadme") or ("_skd_" in filename)
        if not has_valid_contact_section(file_path, is_contact_section_mandatory):
            return False

        if "_skd_" in filename:

            if not check_release_notes_version(file_path):
                return False

            # TODO: Verify Notes and Release history sections

    # TODO: Continue implementation

    return True


def is_an_ingnore_file(file_path):

    filename = os.path.basename(file_path)

    for ignore_pattern in IGNORE_FILES:
        if fnmatch.fnmatch(filename.lower(), ignore_pattern.lower()):
            return True

    return False


def is_kernel_file(file_path):
    if not os.path.isdir(file_path)\
       and not is_an_ingnore_file(file_path):
        extension = str(os.path.splitext(file_path)[1]).lower()
        if extension in CHECK_EXTENSIONS:
            return extension in KERNEL_EXTENSIONS
    return False


def validate_files(files):

    all_files_are_valid = True

    # Check contents file by file
    for filename in files:

        if not os.path.isdir(filename)\
           and not is_an_ingnore_file(filename):

            is_valid_file = True

            extension = str(os.path.splitext(filename)[1]).lower()
            if extension in CHECK_EXTENSIONS:

                if not is_valid_pds_filename(filename):
                    is_valid_file = False

                # CHECK IF IS A DOC FILE
                if extension in DOC_EXTENSIONS:

                    if not is_valid_doc_file(filename):
                        is_valid_file = False
                        log_error("INVALID_DOC_FILE", "Invalid document file.", filename)

                elif extension in KERNEL_EXTENSIONS:

                    # TODO: CHECK IS LATEST VERSION OF THE KERNEL ELSE DO NOTHING

                    if not is_valid_kernel(filename,
                                           CHECK_LINE_LENGTHS, CHECK_INDENTATION, CHECK_TRAILING_CHARS):
                        is_valid_file = False
                        log_error("INVALID_KERNEL_FILE", "Invalid kernel file.", filename)

                if is_valid_file:
                    log_info("VALID_FILE", "File is valid.", filename)

            elif extension not in IGNORE_EXTENSIONS:
                log_error("UNSUPPORTED_EXTENSION", "Extension not supported: " + extension, filename)
                is_valid_file = False

            if not is_valid_file:
                all_files_are_valid = False

            write_file_report(filename)

    return all_files_are_valid


def has_valid_skd_version(skd_path):
    try:
        # Get skd version from version file
        skd_version = get_skd_version(skd_path)
    except Exception as ex:
        log_error("SKD_VERSION", "Error obtaining SKD Version: " + str(ex), skd_path)
        return False

    # Check that all MKs have the correct SKD version
    # note that the MK validity is done by is_valid_metakernel()
    all_mk_files = list(glob.iglob(skd_path + '/**/*.tm', recursive=True))
    all_mk_files += list(glob.iglob(skd_path + '/**/*.TM', recursive=True))
    mk_files = [mk.replace(skd_path + "/", "") for mk in all_mk_files if is_versioned_mk(mk)]

    mks_has_valid_versions = True
    for mk_file in mk_files:
        mk_filename = os.path.basename(mk_file)
        if skd_version not in str(os.path.splitext(mk_filename)[0]).lower():
            log_error("SKD_VERSION", "MK file: '" + str(mk_file) + "' has not the expected SKD version: " + skd_version,
                      skd_path)
            mks_has_valid_versions = False

    # Check that all the release notes files are named properly,
    # note that the release notes files validity is done by is_valid_doc_file()
    release_notes_dir = os.path.join(skd_path, "misc/release_notes")
    if not os.path.exists(release_notes_dir) or not os.path.isdir(release_notes_dir):
        log_error("SKD_VERSION", "Release notes path doesn\'t exist or is not a directory: " + str(release_notes_dir),
                  skd_path)
        return False

    skd_current_path = list(glob.iglob(release_notes_dir + '/*_skd_current.txt', recursive=False))
    if len(skd_current_path) == 0:
        log_error("SKD_VERSION", "Current release notes file not found at path: " + str(release_notes_dir), skd_path)
        return False
    elif len(skd_current_path) > 1:
        log_error("SKD_VERSION", "More than one files matches *_skd_current.txt in release notes path: " +
                  str(release_notes_dir), skd_path)
        return False

    # Check that latest release notes exists and is equal to current, note this is a workaround
    # to commented section below that actually checks all release notes and looks for unexpected files
    skd_current_path = skd_current_path[0]
    skd_current_filename = os.path.basename(skd_current_path)
    version_int = int(skd_version.replace("v", ""))
    rel_note_filename = skd_current_filename.replace("current", "{:03d}".format(version_int))
    rel_note_filepath = os.path.join(release_notes_dir, rel_note_filename)
    release_notes_files = [skd_current_filename ]
    all_release_notes_found = True
    if not os.path.exists(rel_note_filepath):
        log_error("SKD_VERSION", "Release notes file: " + rel_note_filename + " not found at path: "
                  + str(release_notes_dir), skd_path)
        all_release_notes_found = False
    else:
        release_notes_files.append(rel_note_filename)

        # Check tha current release notes files is aligned with latest release notes file
        if not files_are_equal(rel_note_filepath, skd_current_path):
            log_error("SKD_VERSION", "Release notes file: " + rel_note_filename + " is not equal to: "
                      + str(skd_current_filename), skd_path)
            all_release_notes_found = False

    # Check that all release notes exists
    versions = get_versions_history_from_release_notes_file(skd_current_path)
    for version in versions:
        try:
            version_int = int(version.replace("v", "").replace(".", ""))
        except:
            log_error("SKD_VERSION", "Wrong version " + version + " retrieved from: "
                      + skd_current_path + " Release History section", skd_path)
            all_release_notes_found = False
            continue

        rel_note_filename = skd_current_filename.replace("current", "{:03d}".format(version_int))
        rel_note_filepath = os.path.join(release_notes_dir, rel_note_filename)
        if not os.path.exists(rel_note_filepath):
            log_error("SKD_VERSION", "Release notes file: " + rel_note_filename + " not found at path: " +
                      str(release_notes_dir), skd_path)
            all_release_notes_found = False
        else:
            release_notes_files.append(rel_note_filename)

    # Check that in the release_notes directory that are no unexpected files
    all_files = list(glob.iglob(release_notes_dir + '/*', recursive=True))
    unexpected_files = [file
                        for file in all_files
                        if os.path.basename(file) not in release_notes_files]

    for unexpected_file in unexpected_files:
        log_error("SKD_VERSION",  "Unexpected file: " + os.path.basename(unexpected_file) + " found at path: " +
                  str(release_notes_dir) + "\n       Or the corresponding version of " +
                  os.path.basename(unexpected_file) + " is not present at " + skd_current_filename
                  + " Release History section", skd_path)
        all_release_notes_found = False

    return mks_has_valid_versions and all_release_notes_found
