import spiceypy
import datetime

from spiceypy.utils.support_types import SpiceyError


def gen_frame_dict(mk, report=False):
    #
    # Frame names are as follows:
    # r'FRAME_-?[0-9]*_NAME'
    #
    frame_dict = {}

    spiceypy.furnsh(mk)

    start = 1
    n_items = 9999
    template = 'FRAME_*_NAME'
    try:
        cvals = spiceypy.gnpool(template, start, n_items)
        if report: print(f'Number of reference frames defined: {len(cvals)}')
    except SpiceyError:
        print('No frames definitions present')
        return

    #
    # Okay, now we know something about the kernel pool
    # variables of interest to us. Let's find out more...
    #
    for cval in cvals:

        #
        # We check the type of variable:
        # C (character) or N (numeric), of each pool
        # variable name in the cvals array. It has to
        # be a character
        #
        start = 0
        n_items = 20
        [dim, type] = spiceypy.dtpool(cval)

        if type == 'C':
            cvars = spiceypy.gcpool(cval, start, n_items)
            #
            # The variable (list) should be unique
            #
            if len(cvars) > 1:
                spiceypy.kclear()
                raise Exception(f'Variable {cval} is incorrect')

            #
            # We build the frames dictionary
            #
            frmclass = spiceypy.gipool(cval.replace('NAME', 'CLASS'), start,
                                       n_items)
            frmid = spiceypy.gipool(cval.replace('NAME', 'CLASS_ID'), start,
                                       n_items)
            frmcentr = spiceypy.gipool(cval.replace('NAME', 'CENTER'), start,
                                       n_items)

            if frmclass[0] == 4:
                try:
                    varname = cval.replace('FRAME','TKFRAME').replace('NAME', 'RELATIVE')
                    frmrelat = spiceypy.gcpool(varname, start, n_items)
                except:
                    frmrelat = ['ERROR']
            else:
                frmrelat = ['N/A']


            frame_dict[cvars[0]] = { 'name': cvars[0],
                                     'class':frmclass[0],
                                     'id': frmid[0],
                                     'center': frmcentr[0],
                                     'relative': frmrelat[0]
                                    }

            if report:
                print(f'  CLASS: {frmclass[0]}  NAME: {cvars[0]} ')


        else:
            spiceypy.kclear()
            raise Exception(f'Variable {cval} is incorrect')

    spiceypy.kclear()

    return frame_dict


def check(mk, time=False, report=False):

    frames_to_check = False
    if not time:
        today = datetime.datetime.now()
        time = today.strftime("%Y-%m-%dT%H:%M:%S")

    frame_dict = gen_frame_dict(mk, report=report)

    spiceypy.furnsh(mk)
    et = spiceypy.utc2et(time)

    for key in frame_dict.keys():
        if frame_dict[key]['class'] == 4:
            fname = frame_dict[key]['name']
            try:
                spiceypy.pxform(fname, 'J2000', et)
            except SpiceyError:
                frames_to_check = True
                print( f'Frame {fname} not properly defined at {time}\n' +
                       f'   NAME:     {frame_dict[key]["name"]}\n' +
                       f'   CLASS:    {frame_dict[key]["class"]}\n' +
                       f'   ID:       {frame_dict[key]["id"]}\n' +
                       f'   CENTER:   {frame_dict[key]["center"]}\n' +
                       f'   RELATIVE: {frame_dict[key]["relative"]}\n'
                     )
                pass

    spiceypy.kclear()

    if not frames_to_check:
        print(f'All {len(frame_dict)} frames are correct @ {time}')

    return

if __name__ == '__main__':
    mk = '/Users/mcosta/SPICE/BEPICOLOMBO/kernels/mk/bc_ops_local.tm'
    check(mk, report=True)