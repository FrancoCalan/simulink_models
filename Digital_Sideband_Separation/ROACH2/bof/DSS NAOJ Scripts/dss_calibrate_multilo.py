#!/usr/bin/python
# Script for tone calibration of digital sideband separating receiver with 
# multiple LO values and multiple LO stages. Uses the original dss_calibrate.py
# for the heavy-lifting computations, this scripts just extend its functionality
# to multiple LOs.

# imports
import os, time, datetime, tarfile, shutil, json
import numpy as np
import matplotlib.pyplot as plt
import calandigital as cd

# import variables from dss_calibrate to avoid duplication
from dss_calibrate import roach_ip, date_time,  boffile, bandwidth, \
                          nchannels, acc_len, chnl_step, rf_generator_ip, \
                          rf_power, datadir, if_freqs, acc_len_reg, cnt_rst_reg

# import dss_calibrate necessary functions
from dss_calibrate import create_figure, make_dss_measurements

# communication parameters
lo1_generator_ip = None
lo2_generator_ip = None

# experiment parameters
lo1_freqs = range(4, 20, 1) # GHz
lo2_freqs = range(275, 500, 16) # GHz
lo1_power = -50 # dBm
lo2_power = -50 # dBm

def main():
    start_time = time.time()

    make_pre_measurements_actions()
    make_dss_multilo_measurements()
    make_post_measurements_actions()

    print("Finished. Total time: " + str(int(time.time() - start_time)) + "[s]")

def make_pre_measurements_actions():
    """
    Makes all the actions in preparation for the measurements:
    - initizalize ROACH and generator communications.
    - creating plotting and data saving elements
    - setting initial registers in FPGA
    - turning on generator power
    """
    global roach, rf_generator, lo1_generator, lo2_generator
    global fig, line0, line1, line2, line3

    roach = cd.initialize_roach(roach_ip)
    lo1_generator = cd.Instrument(lo1_generator_ip)
    lo2_generator = cd.Instrument(lo1_generator_ip)
    rf_generator  = cd.Instrument(rf_generator_ip)

    print("Setting up plotting and data saving elements...")
    fig, line0, line1, line2, line3 = create_figure()
    make_data_directory()
    print("done")

    print("Setting accumulation register to " + str(acc_len) + "...")
    roach.write_int(acc_len_reg, acc_len)
    print("done")
    print("Resseting counter registers...")
    roach.write_int(cnt_rst_reg, 1)
    roach.write_int(cnt_rst_reg, 0)
    print("done")
    
    print("Setting instruments power and outputs...")
    lo1_generator.write("power " + str(lo1_power))
    lo2_generator.write("power " + str(lo2_power))
    rf_generator.write("power " + str(rf_power))
    lo1_generator.write("outp on")
    lo2_generator.write("outp on")
    rf_generator.write("outp on")
    print("done")

def make_dss_multilo_measurements():
    """
    Makes the measurements for dss calibration with multiple LOs.
    """
    for lo1_freq in lo1_freqs:
        # set lo1 frequency (must be in Hz)
        lo1_generator.ask("freq " + str(lo1_freq*1e9) + ";*opc?")
        
        for lo2_freq in lo2_freqs:
            # set lo2 frequency (must be in Hz)
            lo2_generator.ask("freq " + str(lo2_freq*1e9) + ";*opc?")
            
            # make measurement subdirectory
            measname = "lo1_" + str(lo1_freq) + "ghz_lo2_" + \
                                str(lo2_freq) + "ghz"
            measdir = datadir + "/" + measname
            os.mkdir(measdir)
            
            # compute rf frequencies
            rf_freqs_usb = lo1_freq + lo2_freq + if_freqs
            rf_freqs_lsb = lo1_freq - lo2_freq - if_freqs

            # make measurement
            make_dss_measurements(measdir, rf_freqs_usb, rf_freqs_lsb)

def make_post_measurements_actions():
    """
    Makes all the actions required after measurements:
    - turn off sources
    - compress data
    """
    print("Turning off instruments...")
    lo1_generator.write("outp off")
    lo2_generator.write("outp off")
    rf_generator.write("outp off")
    print("done")

    print("Compressing data...")
    compress_data()
    print("done")

def make_data_directory():
    """
    Make directory where to save all the calibration data.
    """
    os.mkdir(datadir)

    # make .json file with test info
    testinfo = {}
    testinfo["roach ip"]         = roach_ip
    testinfo["date time"]        = date_time
    testinfo["boffile"]          = boffile
    testinfo["bandwidth"]        = bandwidth
    testinfo["nchannels"]        = nchannels
    testinfo["acc len"]          = acc_len
    testinfo["chnl step"]        = chnl_step
    testinfo["lo1 generator ip"] = lo1_generator_ip
    testinfo["lo2 generator ip"] = lo2_generator_ip
    testinfo["lo1 freqs"]        = str(lo1_freqs)
    testinfo["lo2 freqs"]        = str(lo2_freqs)
    testinfo["lo1 power"]        = lo1_power
    testinfo["lo2 power"]        = lo2_power
    testinfo["rf generator ip"]  = rf_generator_ip
    testinfo["rf power"]         = rf_power

    with open(datadir + "/testinfo.json", "w") as f:
        json.dump(testinfo, f, indent=4, sort_keys=True)

def compress_data():
    """
    Compress the data from the datadir directory into a .tar.gz
    file and delete the original directory.
    """
    tar = tarfile.open(datadir + ".tar.gz", "w:gz")
    for datafile in os.listdir(datadir):
        tar.add(datadir + '/' + datafile, datafile)
    tar.close()
    shutil.rmtree(datadir)

if __name__ == '__main__':
    main()
