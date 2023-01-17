import os
import fnmatch

from spival.utils.files import exceeds_line_lengths, has_badchars, is_empty_file
from spival.utils.skd_utils import KERNEL_EXTENSIONS, is_valid_kernel, has_valid_contact_section

IGNORE_FILES = ["earth_??????_*.bpc",
                "gm_de431.tpc",
                "pck00010.tpc",
                "de403_masses.tpc",
                "earth*.tf",
                "MANIFEST.in",
                "README.md",
                "version"]

SHOW_ALL_FILES = False
CHECK_LINE_LENGTHS = True
CHECK_INDENTATION = False
CHECK_TRAILING_CHARS = False

DOC_EXTENSIONS = [".txt", ".csv", ".xml", ".html"]
LONG_LINE_EXTENSIONS = [".csv", ".xml", ".html"]
IGNORE_EXTENSIONS = [".tar", ".obj", ".3ds", ".mtl", ".json", ".png", ".orb", ".gap"]
CHECK_EXTENSIONS = DOC_EXTENSIONS + KERNEL_EXTENSIONS


def is_valid_doc_file(file_path):

    if is_empty_file(file_path):
        print("ERROR!! - EMPTY FILE: " + file_path)
        return False

    if has_badchars(file_path):
        print("ERROR!! - HAS BAD CHARS: " + file_path)
        return False

    basename = os.path.basename(file_path)
    filename, extension = os.path.splitext(basename)
    filename = str(filename).lower()
    extension = str(extension).lower()

    if CHECK_LINE_LENGTHS and not extension in LONG_LINE_EXTENSIONS:
        if exceeds_line_lengths(file_path):
            print("ERROR!! - EXCEEDS LINE LENGTH: " + file_path)
            return False

    if extension == ".txt":
        is_contact_section_mandatory = (filename == "aareadme") or ("_skd_" in filename)
        if not has_valid_contact_section(file_path, is_contact_section_mandatory):
            return False

    # TODO: Continue implementation

    return True


def is_an_ingnore_file(file_path):

    filename = os.path.basename(file_path)

    for ignore_pattern in IGNORE_FILES:
        if fnmatch.fnmatch(filename, ignore_pattern):
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

            extension = str(os.path.splitext(filename)[1]).lower()
            if extension in CHECK_EXTENSIONS:

                # CHECK IF IS A DOC FILE
                if extension in DOC_EXTENSIONS:

                    if not is_valid_doc_file(filename):
                        all_files_are_valid = False
                        print("")
                        continue

                elif extension in KERNEL_EXTENSIONS:

                    if not is_valid_kernel(filename,
                                           CHECK_LINE_LENGTHS, CHECK_INDENTATION, CHECK_TRAILING_CHARS):
                        all_files_are_valid = False
                        print("")
                        continue

                if SHOW_ALL_FILES:
                    print("OK: " + filename)

            elif extension not in IGNORE_EXTENSIONS:

                print("ERROR!! - NOT SUPPORTED: " + filename)
                print("")
                all_files_are_valid = False

    return all_files_are_valid
