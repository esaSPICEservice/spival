import os
import subprocess

def gaps(mk, object_frame, target_frame='J2000'):

    command = f"frmdiff -k {mk} -t dumpg -f1 {target_frame} -t1 {object_frame} -f YYYY-MM-DDTHR:MN:SC ::RND | grep -v ' 0:0[0123]:'"
    print(command)
    command_line_process = subprocess.Popen(command, shell=True,
                                            stdout=subprocess.PIPE,
                                            stderr=subprocess.STDOUT)

    process_output, _ = command_line_process.communicate()

    return process_output.decode("utf-8")


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


#print(gaps_differences('/Users/mcosta/SPICE/ExoMars2016/kernels/mk/em16_ops_local.tm', 'TGO_SPACECRAFT', 'known_gaps.txt'))
#print(gaps('/Users/mcosta/SPICE/ExoMars2016/kernels/mk/em16_ops_local.tm', 'TGO_SPACECRAFT'))




