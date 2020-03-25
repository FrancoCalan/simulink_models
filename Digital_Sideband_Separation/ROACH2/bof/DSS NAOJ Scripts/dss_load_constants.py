#!/usr/bin/python
import argparse, tarfile, time
import numpy as np
import calandigital as cd
from dss_multilo_parameters import *

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
    parser.add_argument("-ct", "--caltar", dest="caltar",
        help=".tar.gz file from where extract the calibration constants.")
    parser.add_argument("-cd", "--caldir", dest="caldir", default="",
        help="Directory within the .tar.gz file where th constants are \
        located. Must end in / if not empty.")
    args = parser.parse_args()

    roach = cd.initialize_roach(args.ip, boffile=args.boffile, upload=args.upload)
    bm_load_constants(roach, args.caltar, args.caldir)

def dss_load_constants(roach, caltar="", caldir=""):
    """
    Load load digital sideband separation constants.
    :param roach: FpgaClient object to communicate with roach.
    :param caltar: .tar.gz file with the calibration data.
    :param caldir: directory with the calibration data within the tar file.
    """
    consts_lsb, consts_usb = compute_consts(caltar, caldir)

    load_comp_constants(roach, consts_usb, bram_consts_usb_re, bram_consts_usb_im)
    load_comp_constants(roach, consts_lsb, bram_consts_lsb_re, bram_consts_lsb_im)

def compute_consts(caltar, caldir):
    """
    Compute constants using tone calibration info.
    :param caltar: calibration .tar.gz file.
    :param caldir: calibration directory.
    :return: calibration constants.
    """
    caldata = get_caldata(caltar, caldir)
    
    # get arrays
    a2_toneusb = caldata['a2_toneusb']; a2_tonelsb = caldata['a2_tonelsb']
    b2_toneusb = caldata['b2_toneusb']; b2_tonelsb = caldata['b2_tonelsb']
    ab_toneusb = caldata['ab_toneusb']; ab_tonelsb = caldata['ab_tonelsb']

    # consts usb are computed with tone in lsb, because you want to cancel out 
    # lsb, the same for consts lsb
    consts_usb =         -1 * ab_tonelsb  / b2_tonelsb #  ab*   / bb* = a/b
    consts_lsb = -1 * np.conj(ab_toneusb) / a2_toneusb # (ab*)* / aa* = a*b / aa* = b/a

    return consts_lsb, consts_usb

def get_caldata(datatar, datadir):
    """
    Extract calibration data from directory compressed as .tar.gz.
    """
    tar_file = tarfile.open(datatar)
    caldata  = np.load(tar_file.extractfile(datadir+'caldata.npz'))

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
