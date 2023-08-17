from spival.command_line import main as spival


def runSPIVAL(debug=False, log=False):

    spival(config='solo.json', debug=debug)


if __name__ == '__main__':
    runSPIVAL(debug=True, log=True)