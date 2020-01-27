from spival.command_line import main as spival


def runSPIVAL(debug=False, log=False):

    spival(config='exomars2016.json', debug=debug)


if __name__ == '__main__':
    runSPIVAL(debug=False, log=True)