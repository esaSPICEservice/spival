import os
import re


def checkOnLabels(path, template):
    f = open(path + '/DOCUMENT/ONLABELS.TXT').readlines()
    defsflag = False
    keywords = []
    for line in f:
        if 'Definition of Keywords/Values for SPICE Kernels' in line:
            defsflag = True
        if defsflag and line[:3] == '   ' and not line[:10] == '          ' and len(line) > 10:
            keywords.append(line.strip().split(' ')[0])
    print(keywords)
    f = open(template).readlines()
    print('\n')
    for line in f:
        if '=' in line:
            if line.split('=')[0].replace(' ', '') not in keywords:
                print('keyword ' + line.split('=')[0].replace(' ', '') + ' missing in ONLABELS.TXT')
    return


def checkFirstLine(path):
    for root, dirs, files in os.walk(path):
        for name in files:
            if name.endswith((".TF", ".TI", ".TLS", ".TSC", ".TPC")):
                f = open(root + '/' + name).readlines()
                if not 'KPL' in f[0]:
                    print('WARNING, FIRST LINE IN FILE: ' + name)
    return


def checkLineLength(path):
    for root, dirs, files in os.walk(path):
        for name in files:
            if not name.endswith((".BSP", ".BC", ".BDS", ".BPC", ".BES", ".ORB", ".TAB", ".DS_Store")):
                f = open(root + '/' + name).readlines()
                for i in range(0, len(f), 1):
                    if len(f[i]) > 79:
                        print('WARNING IN LINE ' + str(i+1) + ': ' + name)
    return


def checkNonAscii(pathroute):
    for path, subdirs, files in os.walk(pathroute):
        for name in files:
            if not name.endswith((".BSP", ".BC", ".BDS", ".BPC", ".BES", ".ORB", ".TAB", ".DS_Store")):
                file = open(os.path.join(path, name), 'r')
                linen = 0
                for line in file.readlines():
                    linen += 1
                    for i in range(0, len(line), 1):
                        e = line[i]
                        if (re.sub('[ -~]', '', e)) != "" and e != '\n':
                            print('non ascii chatacter' + ' - ' + e + ' - ' + 'detected in file: ', name)
                            print('   line: ', linen)
                file.close()
    return


def checkLineEndings(pathroute):
    for path, subdirs, files in os.walk(pathroute):
        for name in files:
            if '.LBL' in name:
                with open(os.path.join(path, name), 'rb') as open_file:
                    content = open_file.read()
                    content = content.replace(b'\r\n', b'\n')
                    content = content.replace(b'\n', b'\r\n')

                with open(os.path.join(path, name), 'wb') as open_file:
                    open_file.write(content)
            elif '.TM' in name:
                with open(os.path.join(path, name), 'rb') as open_file:
                    content = open_file.read()
                    content = content.replace(b'\r\n', b'\n')
                    # content = content.replace(b'\n', b'\r\n')

                with open(os.path.join(path, name), 'wb') as open_file:
                    open_file.write(content)

    return


path = "/Users/aescalante/spice/missions/mex/archives/MEX-E-M-SPICE-6-V2.0"
template = '/Users/aescalante/spice/pipelines/arcgen/arcgen/etc/template_product_spice_kernel.LBL'

checkOnLabels(path=path, template=template)
checkFirstLine(path=path)
checkLineLength(path=path)
checkNonAscii(pathroute=path)
checkLineEndings(pathroute=path)
