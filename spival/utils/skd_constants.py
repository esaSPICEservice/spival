
IGNORE_FILES = ["earth_??????_*.bpc",
                "de432s.bsp",
                "gm_de431.tpc",
                "pck00010.tpc",
                "de*masses.tpc",
                "naif*.tls",
                "earth*.tf",
                "MANIFEST.in",
                "README.md",
                "*.ipynb",
                "*.pdf",
                "version"]

SHOW_ALL_FILES = False
CHECK_LINE_LENGTHS = True
CHECK_INDENTATION = False
CHECK_TRAILING_CHARS = False

KERNEL_TEXT_EXTENSIONS = [".tf", ".ti", ".tls", ".tm", ".tpc", ".tsc"]
KERNEL_BINARY_EXTENSIONS = [".bc", ".bds", ".bpc", ".bsp"]
KERNEL_EXTENSIONS = KERNEL_TEXT_EXTENSIONS + KERNEL_BINARY_EXTENSIONS

DOC_EXTENSIONS = [".txt", ".csv", ".xml", ".html"]
LONG_LINE_EXTENSIONS = [".csv", ".xml", ".html"]

IGNORE_EXTENSIONS = [".tar", ".obj", ".3ds", ".mtl", ".json", ".jpg", ".png", ".orb", ".gap"]
CHECK_EXTENSIONS = DOC_EXTENSIONS + KERNEL_EXTENSIONS

KERNEL_TEXT_HEADERS = {".tf": "KPL/FK",
                       ".ti": "KPL/IK",
                       ".tls": "KPL/LSK",
                       ".tm": "KPL/MK",
                       ".tpc": "KPL/PCK",
                       ".tsc": "KPL/SCLK"}

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

REQUIRED_SECTIONS = {"FK": ["Version and Date",
                            "References",
                            "Contact Information",
                            "Implementation Notes"],
                     "IK": ["Version and Date",
                            "References",
                            "Contact Information",
                            "Implementation Notes",
                            "Naming Conventions",
                            "Mounting Alignment",
                            "Description"],
                     "SPK_PINPOINT": ["Version and Date",
                                      "Contact Information",
                                      "References",
                                      "Related SPICE Kernels",
                                      "Structure location specification -- Definitions",
                                      "Coordinates",
                                      "PINPOINT Input"],
                     "SPK_OEM2SPK": ["Objects",
                                     "Approximate Time Coverage",
                                     "Status",
                                     "Pedigree",
                                     "Usage",
                                     "Accuracy",
                                     "References",
                                     "Contact Information",
                                     "OEM2SPK Setup Parameters"]
                     }

REPLACE_TOKENS = ["id", "name", "used_id"]

FRAME_DEFINITION_KEYWORDS = \
    {
        "frame_class_Any": [
                {
                    "keyword": "FRAME_{name}",
                    "value": "{id}",
                    "line_nr": 0
                },
                {
                    "keyword": "FRAME_{id}_NAME",
                    "value": "{name}",
                    "line_nr": 1
                },
                {
                    "keyword": "FRAME_{used_id}_CLASS",
                    "value": "['1', '2', '3', '4', '5', '6']",
                    "line_nr": 2,
                    "sub_keywords_key": "='frame_class_' + str(value)"
                },
                {
                    "keyword": "FRAME_{used_id}_CLASS_ID",
                    "value": "=str({id}) == str(value) " +
                             "if def_obj['frame_class'] in ['4', '5', '6'] " +
                             "else True",
                    "line_nr": 3
                },
                {
                    "keyword": "FRAME_{used_id}_CENTER",
                    "value": "NAIF_ID",
                    "line_nr": 4
                }
          ],

        "frame_class_1": [],

        "frame_class_2": [],

        "frame_class_3": [
                {
                    "keyword": "CK_{used_id}_SCLK",
                    "value": "=is_number(value)",
                    "line_nr": 5
                },
                {
                    "keyword": "CK_{used_id}_SPK",
                    "value": "=is_number(value)",
                    "line_nr": 6
                }
          ],

        "frame_class_4": [
            {
                "keyword": "TKFRAME_{used_id}_RELATIVE",
                "value": "FRAME_NAME",
                "line_nr": 5
            },
            {
                "keyword": "TKFRAME_{used_id}_SPEC",
                "value": "['MATRIX', 'ANGLES', 'QUATERNION']",
                "line_nr": 6,
                "sub_keywords_key": "='tkframe_specs_' + str(value)"
            }
        ],

        "frame_class_5": [
            {
                "keyword": "FRAME_{used_id}_RELATIVE",
                "value": "FRAME_NAME",
                "line_nr": 5
            },
            {
                "keyword": "FRAME_{used_id}_DEF_STYLE",
                "value": "['PARAMETERIZED']",
                "line_nr": 6
            },
            {
                "keyword": "FRAME_{used_id}_FAMILY",
                "value": "['TWO-VECTOR', 'MEAN_EQUATOR_AND_EQUINOX_OF_DATE', " +
                         " 'TRUE_EQUATOR_AND_EQUINOX_OF_DATE'," +
                         " 'MEAN_ECLIPTIC_AND_EQUINOX_OF_DATE', 'EULER']",
                "line_nr": 7
            }

            # TODO: Define sub_keywords for each FRAME_FAMILY:
            #  https://naif.jpl.nasa.gov/pub/naif/toolkit_docs/C/req/frames.html#Required%20Keywords%20for%20Parameterized%20Dynamic%20Frames
        ],

        "frame_class_6": [
            {
                "keyword": "FRAME_{used_id}_ALIGNED_WITH",
                "value": "FRAME_NAME_LIST",
                "line_nr": 5
            }
        ],

        "tkframe_specs_MATRIX": [
            {
                "keyword": "TKFRAME_{used_id}_MATRIX",
                "value": "=is_spice_vector(value, [float, int], 9)",
                "line_nr": 7
            }
        ],

        "tkframe_specs_ANGLES": [
            {
                "keyword": "TKFRAME_{used_id}_UNITS",
                "value": "['DEGREES', 'RADIANS', 'ARCSECONDS'," +
                         " 'ARCMINUTES' 'HOURANGLE', 'MINUTEANGLE'," +
                         " 'SECONDANGLE']",
                "line_nr": 7
            },
            {
                "keyword": "TKFRAME_{used_id}_AXES",
                "value": "=is_spice_vector(value, int, 3, [1, 2, 3])",
                "line_nr": 8
            },
            {
                "keyword": "TKFRAME_{used_id}_ANGLES",
                "value": "=is_spice_vector(value, [float, int], 3)",
                "line_nr": 9
            }
        ],

        "tkframe_specs_QUATERNION": [
            {
                "keyword": "TKFRAME_{used_id}_Q",
                "value": "=is_spice_vector(value, [float, int], 4)",
                "line_nr": 7
            }
        ]
    }

INSTRUMENT_DEFINITION_KEYWORDS = \
    {
        "instrument_Any": [
                {
                    "keyword": "INS{id}_NAME",
                    "value": "{name}",
                    "line_nr": 0
                },
                {
                    "keyword": "INS{id}_BORESIGHT",
                    "value": "=is_spice_vector(value, [float, int], 3)",
                    "line_nr": 1
                },
                {
                    "keyword": "INS{id}_FOV_FRAME",
                    "value": "FRAME_NAME",
                    "line_nr": 2
                },
                {
                    "keyword": "INS{id}_FOV_SHAPE",
                    "value": "['CIRCLE', 'ELLIPSE', 'RECTANGLE', 'POLYGON']",
                    "line_nr": 3
                },
                {
                    "keyword": "INS{id}_FOV_CLASS_SPEC",
                    "value": "['CORNERS', 'ANGLES']",
                    "line_nr": 4,
                    "optional": "'INS{id}_FOV_BOUNDARY_CORNERS' in keywords",
                    "sub_keywords_key": "='ins_fov_class_specs_' + str(value)"
                },
                {
                    "keyword": "INS{id}_PLATFORM_ID",
                    "value": "=is_spice_vector(value, int, 1)",
                    "optional": "True"
                }
          ],

        "ins_fov_class_specs_CORNERS": [
            {
                "keyword": "INS{id}_FOV_BOUNDARY_CORNERS",
                "value": "=is_spice_vector(value, [float, int], 'len(matrix) % 3 == 0')",
                "line_nr": 5
            }
        ],

        "ins_fov_class_specs_ANGLES": [
            {
                "keyword": "INS{id}_FOV_REF_VECTOR",
                "value": "=is_spice_vector(value, [float, int], 3)",
                "line_nr": 5
            },
            {
                "keyword": "INS{id}_FOV_REF_ANGLE",
                "value": "=is_spice_vector(value, [float, int], 1)",
                "line_nr": 6
            },
            {
                "keyword": "INS{id}_FOV_CROSS_ANGLE",
                "value": "=is_spice_vector(value, [float, int], 1)",
                "optional": "def_obj['fov_shape'] == 'CIRCLE'",
                "line_nr": 7
            },
            {
                "keyword": "INS{id}_FOV_ANGLE_UNITS",
                "value": "['DEGREES', 'RADIANS', 'ARCSECONDS'," +
                         " 'ARCMINUTES', 'HOURANGLE', 'MINUTEANGLE'," +
                         " 'SECONDANGLE']",
            }
        ]
    }

PINPOINT_DEFINITION_KEYWORDS = \
    {
        "sites_Any": [
                {
                    "keyword": "SITES",
                    "value": "=is_spice_vector(value, str, 1, ['{name}'])",
                    "line_nr": 0
                },
                {
                    "keyword": "{name}_IDCODE",
                    "value": "=is_number(value)",
                    "line_nr": 1
                },
                {
                    "keyword": "{name}_CENTER",
                    "value": "NAIF_ID",
                    "line_nr": 2
                },
                {
                    "keyword": "{name}_FRAME",
                    "value": "FRAME_NAME",
                    "line_nr": 3
                },
                {
                    "keyword": "{name}_XYZ",
                    "value": "=is_spice_vector(value, [float, int], 3)",
                    "line_nr": 4
                },
                {
                    "keyword": "{name}_BOUNDS",
                    "value": "=is_spice_vector(value, 'date_str', 2)",
                    "line_nr": 5
                }
          ],
    }
