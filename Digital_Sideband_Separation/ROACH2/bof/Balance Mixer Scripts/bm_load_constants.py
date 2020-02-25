import argparse
import calandigital as cd

parser = argparse.ArgumentParser(
    description="Load calibration constants from a compressed file or \
        command line input.")
parser.add_argument("-i", "--ip", dest="ip", required=True,
    help="ROACH IP address.")
parser.add_argument("-b", "--bof", dest="boffile",
    help="Boffile to load into the FPGA.")
parser.add_argument("-u", "--upload", dest="upload", action="store_true",
    help="If used, upload .bof from PC memory (ROACH2 only).")
parser.add_argument("-cd", "--caldir", dest="caldir", default=None,
    help="Directory from where extract the calibration constants. Assumes it \
        is compressed in .tar.gz format.")
parser.add_argument("-id", "--ideal", dest="ideal", default="1",
    help="Ideal constant to load. Used if no calibration directory is given.")

# model parameters
nchannels      = 2048
consts_nbits   = 32
consts_binpt   = 27
bram_consts_cancel_re = ['bram_mult0_0_bram_re', 'bram_mult0_1_bram_re',
                         'bram_mult0_2_bram_re', 'bram_mult0_3_bram_re',
                         'bram_mult0_4_bram_re', 'bram_mult0_5_bram_re',
                         'bram_mult0_6_bram_re', 'bram_mult0_7_bram_re']
bram_consts_cancel_im = ['bram_mult0_0_bram_im', 'bram_mult0_1_bram_im',
                         'bram_mult0_2_bram_im', 'bram_mult0_3_bram_im',
                         'bram_mult0_4_bram_im', 'bram_mult0_5_bram_im',
                         'bram_mult0_6_bram_im', 'bram_mult0_7_bram_im']
bram_consts_add_re    = ['bram_mult1_0_bram_re', 'bram_mult1_1_bram_re',
                         'bram_mult1_2_bram_re', 'bram_mult1_3_bram_re',
                         'bram_mult1_4_bram_re', 'bram_mult1_5_bram_re',
                         'bram_mult1_6_bram_re', 'bram_mult1_7_bram_re']
bram_consts_add_im    = ['bram_mult1_0_bram_im', 'bram_mult1_1_bram_im',
                         'bram_mult1_2_bram_im', 'bram_mult1_3_bram_im',
                         'bram_mult1_4_bram_im', 'bram_mult1_5_bram_im',
                         'bram_mult1_6_bram_im', 'bram_mult1_7_bram_im']

def main():
    args = parser.parse_args()

    roach = cd.initialize_roach(args.ip, boffile=args.boffile, upload=args.upload)

    if args.caldir is not None:
        print("Using constants from calibration directory.")
        if args.caldir.startswith("bm_cal_tone"):
            print("Computing constants from tone calibration.")
            consts = compute_tone_consts(args.caldir)

        elif args.caldir.startswith("bm_cal_noise"):
            print("Computing constants from noise calibration.")
            consts = compute_noise_consts(args.caldir)

        else:
            print("Unable to get calibration time :(")
            exit()

    else: # use ideal constants
        print("Using ideal constant " + args.ideal + ".")
        consts = complex(args.ideal) * np.ones(nchannels, dtype=np.complex64)

    print("Loading constants...")
    load_comp_constants(roach,    consts, bram_consts_cancel_re, bram_consts_cancel_im)
    load_comp_constants(roach, -1*consts, bram_consts_add_re,    bram_cancel_add_im)
    print("done")

def compute_tone_consts(caldir):
    """
    Compute constants using tone calibration info.
    :param caldir: calibration directory.
    :return: calibration constants.
    """
    caldata = get_caldata(caldir)
    
    # get arrays
    a2_usb = caldata['a2_usb']; a2_lsb = caldata['a2_lsb']
    b2_usb = caldata['b2_usb']; b2_lsb = caldata['b2_lsb']
    ab_usb = caldata['ab_usb']; ab_lsb = caldata['ab_lsb']

    #consts = -1.0 * ab_usb / b2_usb
    #consts = -1.0 * ab_lsb / b2_lsb
    # use combination of lsb and usb
    consts = -1.0 *  (ab_usb + ab_lsb) / (b2_usb + b2_lsb)

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

def get_datacal(datadir):
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
    cd.write_interleaved_data(roach, bram_re, 8, consts_re_fixed)
    cd.write_interleaved_data(roach, bram_im, 8, consts_im_fixed)

if __name__ == '__main__':
    main()
