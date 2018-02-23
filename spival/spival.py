#!/usr/bin/env python3
from spiops import spiops

def spival(config):

    with open('temp.mk', 'w') as tm:

        with open(config['skd_path']+ '/mk/' + config['mk'], 'r') as f:
            for line in f:
                if "'..'" in line:
                    line = line.replace("'..'",
                                        "'"+config['skd_path']+"'")
                tm.write(line)

    spiops.load('temp.mk')

    spk_list = []

    with open('temp.mk', 'r') as f:
        for line in f:
            if '.bsp' in line.lower():
                spk_list.append(line.split('/')[-1].strip()[:-1])

    for spk in spk_list:
        test_cov_spk(spk=config['skd_path']+'/spk/'+spk)


    return

def test_cov_spk(spk):

    cov = spiops.cov_spk_ker(spk=spk,
                             time_format='UTC')

    print('Coverage for',spk)
    index = 0
    for element in cov[0]:
        print(element, cov[1][index])
        index += 1

    return