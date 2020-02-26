import argparse, tarfile, os
import numpy as np
import calandigital as cd

# model parameters
nchannels      = 2048
consts_nbits   = 32
consts_binpt   = 27
# constants where RF is maximized (LO is rejected)
bram_consts_rf_re = ['bram_mult0_0_bram_re', 'bram_mult0_1_bram_re',
                     'bram_mult0_2_bram_re', 'bram_mult0_3_bram_re',
                     'bram_mult0_4_bram_re', 'bram_mult0_5_bram_re',
                     'bram_mult0_6_bram_re', 'bram_mult0_7_bram_re']
bram_consts_rf_im = ['bram_mult0_0_bram_im', 'bram_mult0_1_bram_im',
                     'bram_mult0_2_bram_im', 'bram_mult0_3_bram_im',
                     'bram_mult0_4_bram_im', 'bram_mult0_5_bram_im',
                     'bram_mult0_6_bram_im', 'bram_mult0_7_bram_im']
# constants where LO is maximized (RF is rejected)
bram_consts_lo_re = ['bram_mult1_0_bram_re', 'bram_mult1_1_bram_re',
                     'bram_mult1_2_bram_re', 'bram_mult1_3_bram_re',
                     'bram_mult1_4_bram_re', 'bram_mult1_5_bram_re',
                     'bram_mult1_6_bram_re', 'bram_mult1_7_bram_re']
bram_consts_lo_im = ['bram_mult1_0_bram_im', 'bram_mult1_1_bram_im',
                     'bram_mult1_2_bram_im', 'bram_mult1_3_bram_im',
                     'bram_mult1_4_bram_im', 'bram_mult1_5_bram_im',
                     'bram_mult1_6_bram_im', 'bram_mult1_7_bram_im']

if __name__ == '__main__':
    # if used as main script, read command line argmuments 
    # and starts roach communication
    parser = argparse.ArgumentParser(
        description="Load calibration constants from a compressed file or \
            command line input.")
    parser.add_argument("-i", "--ip", dest="ip", required=True,
        help="ROACH IP address.")
    parser.add_argument("-b", "--bof", dest="boffile",
        help="Boffile to load into the FPGA.")
    parser.add_argument("-u", "--upload", dest="upload", action="store_true",
        help="If used, upload .bof from PC memory (ROACH2 only).")
    parser.add_argument("-li", "--load_ideal", dest="load_ideal", action="store_true",
        help="If used, load ideal constant, else use calibration constants \
        from caldir.")
    parser.add_argument("-ic", "--ideal_const", dest="ideal_const", default="1",
        help="Ideal constant to load value to load.")
    parser.add_argument("-cd", "--caldir", dest="caldir",
        help="Directory from where extract the calibration constants. \
        Assumes it is compressed in .tar.gz format.")
    args = parser.parse_args()

    roach = cd.initialize_roach(args.ip, boffile=args.boffile, upload=args.upload)
    dbm_load_constants(roach, args.load_ideal, complex(args.ideal_const), args.caldir)

def dbm_load_constants(roach, load_ideal, ideal_const=1+0j, caldir=""):
    """
    Load load digital balance mixer constants.
    :param roach: FpgaClient object to communicate with roach.
    :param load_ideal: if True, load ideal constant, else use calibration 
        constants from caldir.
    :param ideal_const: ideal constant value to load.
    :param caldir: .tar.gz directory with the calibration data.
    """
    if load_ideal:
        print("Using ideal constant " + str(ideal_const) + ".")
        consts = ideal_const * np.ones(nchannels, dtype=np.complex64)
    else: # use calibrated constants
        print("Using constants from calibration directory.")
        if caldir.startswith("dbm_cal_tone"):
            print("Computing constants from tone calibration.")
            consts = compute_tone_consts(caldir)

        elif caldir.startswith("dbm_cal_noise"):
            print("Computing constants from noise calibration.")
            consts = compute_noise_consts(caldir)

        else:
            print("Unable to get calibration time :(")
            exit()

    print("Loading constants...")
    load_comp_constants(roach,    consts, bram_consts_rf_re, bram_consts_rf_im)
    load_comp_constants(roach, -1*consts, bram_consts_lo_re, bram_consts_lo_im)
    print("done")

def compute_tone_consts(caldir):
    """
    Compute constants using tone calibration info.
    :param caldir: calibration directory.
    :return: calibration constants.
    """
    caldata = get_caldata(caldir)
    
    # get arrays
    a2_toneusb = caldata['a2_toneusb']; a2_tonelsb = caldata['a2_tonelsb']
    b2_toneusb = caldata['b2_toneusb']; b2_tonelsb = caldata['b2_tonelsb']
    ab_toneusb = caldata['ab_toneusb']; ab_tonelsb = caldata['ab_tonelsb']

    #consts = -1.0 * ab_usb / b2_usb
    #consts = -1.0 * ab_lsb / b2_lsb
    # use combination of lsb and usb
    consts = -1.0 *  (ab_toneusb + ab_tonelsb) / (b2_toneusb + b2_tonelsb)

    return consts

def compute_noise_consts(caldir):
    """
    Compute constants using noise calibration info.
    :param caldir: calibration directory.
    :return: calibration constants.
    """
    caldata = get_caldata(caldir)
    consts = -1 * caldata['ab']  / caldata['b2'] # -ab* / bb* = -a/b

    return consts

def get_caldata(datadir):
    """
    Extract calibration data from directory compressed as .tar.gz.
    """
    tar_file = tarfile.open(datadir)
    tar_file.extract('caldata.npz')
    caldata = np.load('caldata.npz')
    os.remove('caldata.npz')

    return caldata

def load_comp_constants(roach, consts, bram_re, bram_im):
    """
    Load complex constants into ROACH bram. Real and imaginary parts
    are loaded in separated bram blocks.
    :param roach: FpgaClient object to communicate with roach
    :param consts: complex constants array.
    :param bram_re: bram block name for real part.
    :param bram_im: bram block name for imaginary part.
    """
    # separate real and imaginary
    consts_re = np.real(consts)
    consts_im = np.imag(consts)

    # convert data into fixed point representation
    consts_re_fixed = cd.float2fixed(consts_re, consts_nbits, consts_binpt, warn=True)
    consts_im_fixed = cd.float2fixed(consts_im, consts_nbits, consts_binpt, warn=True)

    # load data
    cd.write_interleaved_data(roach, bram_re, consts_re_fixed)
    cd.write_interleaved_data(roach, bram_im, consts_im_fixed)
