

LOGS = {}

LOG_LEVEL_INFO = "Info"
LOG_LEVEL_WARN = "Warning"
LOG_LEVEL_ERROR = "Error"
LOG_LEVELS = [LOG_LEVEL_INFO, LOG_LEVEL_WARN, LOG_LEVEL_ERROR]

LOG_TYPES = ["EMPTY_FILE", "HAS_BAD_CHARS", "BAD_CHAR", "HAS_LONG_LINES", "EXCEEDS_LINE_LENGTH", "WRONG_CONTACT",
             "INVALID_DOC_FILE", "INVALID_KERNEL_FILE", "INVALID_TEXT_KERNEL", "INVALID_BINARY_KERNEL",
             "INVALID_METAKERNEL", "WRONG_KERNEL_EXTENSION", "VALID_FILE", "UNSUPPORTED_EXTENSION", "SKD_VERSION",
             "INVALID_FRAMES_KERNEL", "INVALID_INSTRUMENTS_KERNEL", "HAS_WRONG_INDENTATION", "HAS_TRAILING_CHARS",
             "TRAILING_CHARS", "INVALID_CK_KERNEL", "INVALID_SPK_KERNEL", "WRONG_MK", "WRONG_KERNEL_HEADER",
             "WRONG_VERSION_SECTION", "WRONG_RELEASE_NOTES", "DATA_AND_COMMENTS", "MISSING_SECTION", "NAIF_IDS",
             "WRONG_DEFINITIONS", "MISALIGNED_SECTION", "WRONG_INDENTATION", "WRONG_KEYWORD", "WRONG_KEYWORD_ORDER"]


def add_log(level, l_type, message, path):

    if path not in LOGS:
        LOGS[path] = []

    LOGS[path].append({"level": level,
                       "type": l_type,
                       "message": message})

    print(level + " - " + l_type + " -> " + message + " - " + path)


def log_info(l_type, message, path):
    add_log(LOG_LEVEL_INFO, l_type, message, path)


def log_warn(l_type, message, path):
    add_log(LOG_LEVEL_WARN, l_type, message, path)


def log_error(l_type, message, path):
    add_log(LOG_LEVEL_ERROR, l_type, message, path)


def write_file_report(path):

    if path in LOGS:

        level_counts = {}
        for log_level in LOG_LEVELS:
            level_counts[log_level] = 0

        log_type_counts = {}
        for log_type in LOG_TYPES:
            log_type_counts[log_type] = 0

        for log in LOGS[path]:
            level_counts[log["level"]] += 1
            log_type_counts[log["type"]] += 1

        print("--------------------------------------------------------")
        print(" ===> " + path)
        print("")

        for log_level in LOG_LEVELS:
            print("        " + log_level + ": " + str(level_counts[log_level]))
        print("")

        for log_type in LOG_TYPES:
            counts = log_type_counts[log_type]
            if counts > 0:
                print("        " + log_type + ": " + str(counts))
        print("")

        print("--------------------------------------------------------")
        print("")


def write_final_report(path_arr, num_files):

    level_counts = {}
    for log_level in LOG_LEVELS:
        level_counts[log_level] = 0

    log_type_counts = {}
    for log_type in LOG_TYPES:
        log_type_counts[log_type] = 0

    for path in LOGS:
        for log in LOGS[path]:
            level_counts[log["level"]] += 1
            log_type_counts[log["type"]] += 1

    print("--------------------------------------------------------")
    print("    SKD VALIDATION REPORT:")
    print("--------------------------------------------------------")
    print("")
    print("  PATHS: " + str(path_arr))
    print("  NUMBER OF FILES: " + str(num_files))
    print("")

    for log_level in LOG_LEVELS:
        print("        " + log_level + ": " + str(level_counts[log_level]))
    print("")

    for log_type in LOG_TYPES:
        counts = log_type_counts[log_type]
        if counts > 0:
            print("        " + log_type + ": " + str(counts))
    print("")

    print("--------------------------------------------------------")
    print("")
