#!/usr/bin/env python3


import os
import json
import textwrap
import traceback
import glob


from argparse import ArgumentParser, RawDescriptionHelpFormatter

from spival.core.skd import check
from spival.core.skd import write_ExoMars2016
from spival.core.skd import write_BepiColombo
from spival.core.skd import write_MarsExpress
from spival.utils import frames
from spival.utils import coverage
from spival.utils import utils


def main(config=False, debug=False, log=False, mission=False):

    execution_dir = os.getcwd()

    with open(os.path.dirname(__file__) + '/config/version',
              'r') as f:
        for line in f:
            version = line

    parser = ArgumentParser(formatter_class=RawDescriptionHelpFormatter,
                                description=textwrap.dedent('''\

 SPIVAL -- Version {}, SPICE Kernel Dataset Validation Pipeline 

   SPIVAL is a library aimed to validate SPICE Kernel Datasets (SKDs) 
   for ESA Planetary missions. More information is available here:

      https://github.com/esaSPICEservice/spival

'''.format(version)),
                                epilog='''
  If SPIVAL is run without any parameter on a directory it performs a full
  SKD Consistency check.                              
  
                                
    __   __   __      __   __     __   ___     __   ___  __          __   ___
   /__\ /__` '__\    /__` |__) | /  ` |__     /__` |__  |__) \  / | /  ` |__
   \__, .__/ \__/    .__/ |    | \__, |___    .__/ |___ |  \  \/  | \__, |___

 esa_spice@sciops.esa.int
 http://spice.esac.esa.int

''')
    parser.add_argument('-v', '--version',
                        help='Display the version of SPIVAL',
                        action='store_true')
    parser.add_argument('-ch', '--check',
                        help='Quick check on the current directory',
                        action='store_true')
    parser.add_argument('-m', '--metakernel',
                        help='Meta-kernel to be read',
                        default='stdout')
    parser.add_argument('-t', '--time',
                        help='UTC time to consider for validation e.g.: 2019-12-13T00:00:00',
                        default='stdout')
    parser.add_argument('-f', '--frames',
                        help='Check reference frames validity',
                        action='store_true')
    parser.add_argument('-c', '--coverage',
                        help='Check reference frames coverage',
                        action='store_true')
    parser.add_argument('-of', '--object_frame',
                        help='Specify object reference',
                        default='stdout')
    parser.add_argument('-tf', '--target_frame',
                        help='Specify object reference',
                        default='stdout')
    parser.add_argument('-g', '--gaps',
                        help='Check coverage gaps with an already existing report',
                        default='stdout')
    parser.add_argument('-rf', '--report_frames',
                        help='Report certain messages of the "--frames" execution',
                        action='store_true')
    parser.add_argument('-cf', '--config',
                        help='Configuration to run full pipeline for a project',
                        default='stdout')
    parser.add_argument('-pp', '--postprocessing',
                        help='Runs post-processing actions over exported Jupyter Notebooks to HTML',
                        default='stdout')
    args = parser.parse_args()

    if args.version:
        print(version)
        return

    if args.postprocessing != 'stdout':
        html_files = glob.glob(args.postprocessing)
        for html_file in html_files:
            utils.post_process_html(html_file)
        return

    if args.metakernel: mk = args.metakernel
    if args.time: time = args.time
    if args.gaps: gaps = args.gaps
    if not args and args.config: config = args.config
    if not args.time: time = False

    if args.frames:
        frames.check(mk, time, args.report_frames)
        return

    if args.coverage:
        if args.target_frame != 'stdout':
            target_frame = args.target_frame
            print(type(target_frame))
        else:
            target_frame = 'J2000'
        print(coverage.gaps(args.object_frame, target_frame=target_frame, mk=mk))
        return

    if args.gaps != 'stdout':
        if args.target_frame != 'stdout':
            target_frame = args.target_frame
        else:
            target_frame = 'J2000'
        print(coverage.gaps_differences(mk, args.object_frame, gaps, target_frame=target_frame))
        return

    if args.check:
        return check()

    if args.config != 'stdout':
        config = args.config

    #
    # We load the configuration
    #
    try:
        with open(config) as f:
            try:
                config = json.load(f)
                root_dir = os.path.dirname(__file__)
                config['root_dir'] = root_dir
                mission = config['mission']
            except:
                error_message = str(traceback.format_exc())
                print("Error: The SPIVAL JSON configuration file has syntactical errors.")
                print(error_message)
                raise

            if mission.lower() == 'exomars2016':
                write_ExoMars2016(config)
            if mission.lower() == 'bepicolombo':
                write_BepiColombo(config)
            if mission.lower() == 'mars_express':
                write_MarsExpress(config)

    except:
        #
        # This needs to be completed by a validation of the JSON file
        #
        print('Info: The SPIVAL configuration file has not been provided.')
        raise

    return