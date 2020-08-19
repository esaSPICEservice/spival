import os
import io
import spiceypy
import numpy as np

import gnuplotlib as gp
import more_itertools as mit
import matplotlib.pyplot as plt


import subprocess

from io import StringIO
import sys



def gaps(object_frame, target_frame='J2000', minimum_duration='',
         mk='', lsk='', sclk='', fk='', ck=''):

    if mk:
        kernels = mk
        kernel = mk.split(os.sep)[-1]
        spiceypy.furnsh(mk)
    else:
        kernels = f'{lsk} {sclk} {fk} {ck}'
        kernel = ck.split(os.sep)[-1]
        spiceypy.furnsh(lsk)

    if minimum_duration:
        minimum_duration = "| grep -v ' 0:0[0123]:'"

    command = f"frmdiff -k {kernels} -t dumpg -f1 {target_frame} -t1 {object_frame} -f YYYY-MM-DDTHR:MN:SC ::UTC  {minimum_duration}"
    print(command)
    command_line_process = subprocess.Popen(command, shell=True,
                                            stdout=subprocess.PIPE,
                                            stderr=subprocess.STDOUT)

    process_output, _ = command_line_process.communicate()

    frmdiff_output = process_output.decode("utf-8")
    frmdiff_output = frmdiff_output.split('\n')
    gap_durations = []
    for line in frmdiff_output:
        if "#    from" in line and 'TDB seconds' in line:
            start_time = float(line.split("(")[1].split()[0])
        if "#    to" in line and 'TDB seconds'in line:
            stop_time = float(line.split("(")[1].split()[0])
        if '#' not in line:
            try:
                gap_durations.append(float(line.split()[2]))

            except:
                pass

    gap_durations = np.array(gap_durations)
    gap_duration = np.sum(gap_durations)
    total_duration = stop_time - start_time
    gap_percentage = gap_duration / total_duration * 100
    start_utc = spiceypy.et2utc(start_time, 'ISOC', 2, 80)
    stop_utc = spiceypy.et2utc(stop_time, 'ISOC', 2, 80)


    bins = 12
    header = f"# ESA SPICE Service gap report file for ExoMars2016\n#\n# Gap Report for {kernel}\n#\n" \
             f"#   Coverage Start:  '{start_utc}' UTC\n" \
             f"#   Coverage Stop:   '{stop_utc}' UTC\n#\n"
    try:
        binwidth = np.max(gap_durations)/(bins-1)
        dur_hist, bins = np.histogram(gap_durations, bins=bins)


        gp.plot((gap_durations, dict(histogram='freq', binwidth=binwidth)),
                    terminal='dumb 75,17', output='temp.txt',
                    unset='grid')

        header += f"# Gaps: {np.size(gap_durations)}\n#\n" \
                  f"#    Gaps duration: {gap_duration:.2f}s \n" \
                  f"#    Data duration: {total_duration:.2f}s\n" \
                  f"#    Gaps/Data:     {gap_percentage:3.2f}% \n#\n" \
                  f"# Gaps Histogram (Bins in hours):\n" \
                  f"#   "+" "*len(f"{bins[0]/60/60:02.2f}")

        index = 0
        for gap_count in dur_hist:
            num_char = len(f"{bins[index] / 60 / 60:02.2f}") - 1
            header += f"{gap_count:02}" + " " * num_char
            index += 1
        header += '\n#   '
        for bin in bins:
            header += f"{bin / 60 / 60:02.2f} "

        header += "\n#\n# Number of Gaps\n"

        with open('temp.txt', 'r') as p:
            for line in p:
                if line.strip():
                    header += f'# {line}'

        header += "#" + " " * 25 + "Gap Bin Duration in seconds\n"

        os.remove('temp.txt')

    except:
        pass

    header += "#\n# gap_start         gap_stop              gap_duration_sec   gap_duration_string\n"
    header += "# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - \n"
    output = header

    for line in frmdiff_output:
        if '#' not in line:
            output += line + '\n'

    spiceypy.kclear()

    return output



def gaps_differences(mk, object_frame, known_gaps, target_frame='J2000'):

    gaps_string = gaps(mk, object_frame, target_frame)
    gaps_string = gaps_string.split('\n')

    gaps_list = []
    known_gaps_list = []

    for line in gaps_string:
        if '#' not in line:
            gaps_list.append(line)

    with open(known_gaps, 'r') as f:
        for line in f:
            if '#' not in line:
                known_gaps_list.append(line.split('\n')[0])

    new_gaps = list(set(gaps_list) - set(known_gaps_list))
    new_gaps.sort()

    if not new_gaps:
        return False

    new_gaps_string = f'#\n# Coverage comparison with gaps from: {known_gaps}\n'
    for line in gaps_string:
        if "#" in line: new_gaps_string += line+'\n'
    for line in new_gaps:
        new_gaps_string += line + '\n'

    return new_gaps_string


if __name__ == '__main__':

    #print(gaps_differences('/Users/mcosta/SPICE/ExoMars2016/kernels/mk/em16_ops_local.tm', 'TGO_SPACECRAFT', 'known_gaps.txt'))
    #output  = gaps('TGO_SPACECRAFT',mk='/Users/mcosta/adcsng/adcsng/tests/em16/ker_gen/mk/em16_ops_v100_20200410_001.tm')
    #output  = gaps('TGO_SPACECRAFT',lsk ='/Users/mcosta/em16_spice/002/em16_spice/spice_kernels/lsk/naif0012.tls',
    #               sclk = '/Users/mcosta/em16_spice/002/staging/kernels/sclk/em16_tgo_step_20191109.tsc',
    #               fk = '/Users/mcosta/em16_spice/002/em16_spice/spice_kernels/fk/em16_tgo_v18.tf', ck = '/Users/mcosta/em16_spice/002/staging/kernels/ck/em16_tgo_sc_ssm_20190101_20200101_s20191109_v01.bc')
    output  = gaps('VEX_SPACECRAFT',mk='/Users/mcosta/PDS3_vex_review/VEX-E-V-SPICE-6-V2.0/EXTRAS/MK/VEX_V01.TM')

    with open("VEX_V01.txt", "w") as text_file:
        text_file.write(output)

    print(output)





