#!/usr/bin/python
# Script for tone calibration of digital sideband separating receiver. Computes 
# the magnitude ratio and phase difference of backend by sweeping a tone with 
# a signal generator.
# It then saves the data into a compress folder, for later be used as 
# calibration constants with an srr computation script.

# imports
import os, time, tarfile, shutil, json
import numpy as np
import matplotlib.pyplot as plt
import calandigital as cd
from dss_parameters import *

def main():
    start_time = time.time()

    make_pre_measurements_actions()
    make_dss_measurements()
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
    global roach, rf_generator, fig, lines

    roach = cd.initialize_roach(roach_ip)
    rf_generator = rm.open_resource(rf_generator_name)

    print("Setting up plotting and data saving elements...")
    fig, lines = create_figure()
    make_data_directory()
    print("done")

    print("Setting accumulation register to " + str(acc_len) + "...")
    roach.write_int(cal_acc_len_reg, acc_len)
    print("done")
    print("Resseting counter registers...")
    roach.write_int(cnt_rst_reg, 1)
    roach.write_int(cnt_rst_reg, 0)
    print("done")
    
    print("Setting instruments power and outputs...")
    rf_generator.write("power " + str(rf_power))
    rf_generator.write("outp on")
    print("done")

def make_dss_measurements():
    """
    Makes the measurements for dss calibration.
    """
    print("Starting tone sweep in upper sideband...")
    sweep_time = time.time()
    a2_toneusb, b2_toneusb, ab_toneusb = get_caldata(rf_freqs_usb, "usb")
    print("done (" +str(int(time.time() - sweep_time)) + "[s])")
        
    print("Starting tone sweep in lower sideband...")
    sweep_time = time.time()
    a2_tonelsb, b2_tonelsb, ab_tonelsb = get_caldata(rf_freqs_lsb, "lsb")
    print("done (" +str(int(time.time() - sweep_time)) + "[s])")

    print("Saving data...")
    np.savez(cal_datadir+"/caldata", 
        a2_toneusb=a2_toneusb, b2_toneusb=b2_toneusb, ab_toneusb=ab_toneusb,
        a2_tonelsb=a2_tonelsb, b2_tonelsb=b2_tonelsb, ab_tonelsb=ab_tonelsb)
    print("done")

    print("Printing data...")
    print_data()
    print("done")

def make_post_measurements_actions():
    """
    Makes all the actions required after measurements:
    - turn off sources
    - compress data
    """
    print("Turning off instruments...")
    rf_generator.write("outp off")
    print("done")

    print("Compressing data...")
    compress_data(cal_datadir)
    print("done")

def create_figure():
    """
    Creates figure for plotting.
    """
    fig, [[ax0, ax1], [ax2, ax3]] = plt.subplots(2,2)
    fig.set_tight_layout(True)
    fig.show()
    fig.canvas.draw()
    
    # get line objects
    line0, = ax0.plot([],[])
    line1, = ax1.plot([],[])
    line2, = ax2.plot([],[])
    line3, = ax3.plot([],[])
    lines  = [line0, line1, line2, line3] 
    
    # set spectrometers axes
    ax0.set_xlim((0, bandwidth))     ; ax1.set_xlim((0, bandwidth))
    ax0.set_ylim((-85, 5))           ; ax1.set_ylim((-85, 5))
    ax0.grid()                       ; ax1.grid()
    ax0.set_xlabel('Frequency [MHz]'); ax1.set_xlabel('Frequency [MHz]')
    ax0.set_ylabel('Power [dBFS]')   ; ax1.set_ylabel('Power [dBFS]')
    ax0.set_title('ZDOK0 spec')      ; ax1.set_title('ZDOK1 spec')

    # set magnitude diference axis
    ax2.set_xlim((0, bandwidth))
    ax2.set_ylim((0, 2))     
    ax2.grid()                 
    ax2.set_xlabel('Frequency [MHz]')
    ax2.set_ylabel('Mag ratio [lineal]')     

    # set magnitude diference axis
    ax3.set_xlim((0, bandwidth))
    ax3.set_ylim((-200, 200))     
    ax3.grid()                 
    ax3.set_xlabel('Frequency [MHz]')
    ax3.set_ylabel('Angle diff [degrees]')

    return fig, lines

def make_data_directory():
    """
    Make directory where to save all the calibration data.
    """
    os.mkdir(cal_datadir)

    # make .json file with test info
    testinfo = {}
    testinfo["roach ip"]          = roach_ip
    testinfo["date time"]         = date_time
    testinfo["boffile"]           = boffile
    testinfo["bandwidth mhz"]     = bandwidth
    testinfo["nchannels"]         = nchannels
    testinfo["acc len"]           = acc_len
    testinfo["chnl step"]         = chnl_step
    testinfo["lo freq ghz"]       = lo_freq
    testinfo["rf generator name"] = rf_generator_name
    testinfo["rf power dbm"]      = rf_power

    with open(cal_datadir + "/testinfo.json", "w") as f:
        json.dump(testinfo, f, indent=4, sort_keys=True)

    # make rawdata folders
    os.mkdir(cal_datadir + "/rawdata_tone_usb")
    os.mkdir(cal_datadir + "/rawdata_tone_lsb")

def get_caldata(rf_freqs, tone_sideband):
    """
    Sweep a tone through a sideband and get the calibration data.
    The calibration data is the power of each tone in both inputs (a and b)
    and the cross-correlation of both inputs as a complex number (ab*).
    The full sprecta measured for each tone is saved to data for debugging
    purposes.
    :param rf_freqs: frequencies of the tones to perform the sweep (in GHz).
    :param tone_sideband: sideband of the injected test tone. Either USB or LSB
    :return: calibration data: a2, b2, and ab.
    """
    fig.canvas.set_window_title(tone_sideband.upper() + " Tone Sweep")

    a2_arr = []; b2_arr = []; ab_arr = []
    for i, chnl in enumerate(test_channels):
        # set test tone
        freq = rf_freqs[chnl]
        rf_generator.ask("freq " + str(freq) + " ghz; *opc?")
        time.sleep(pause_time)

        # read data
        a2    = cd.read_interleave_data(roach, bram_a2,    bram_addr_width, 
                                        bram_word_width,   pow_data_type)
        b2    = cd.read_interleave_data(roach, bram_b2,    bram_addr_width, 
                                        bram_word_width,   pow_data_type)
        ab_re = cd.read_interleave_data(roach, bram_ab_re, bram_addr_width, 
                                        bram_word_width,   crosspow_data_type)
        ab_im = cd.read_interleave_data(roach, bram_ab_im, bram_addr_width, 
                                        bram_word_width,   crosspow_data_type)

        # append data to arrays
        a2_arr.append(a2[chnl])
        b2_arr.append(b2[chnl])
        ab_arr.append(ab_re[chnl] + 1j*ab_im[chnl])

        # scale and dBFS data for plotting
        a2_plot = cd.scale_and_dBFS_specdata(a2, acc_len, dBFS)
        b2_plot = cd.scale_and_dBFS_specdata(b2, acc_len, dBFS)

        # compute input ratios for plotting
        ab_ratios = np.divide(ab_arr, b2_arr)

        # plot data
        lines[0].set_data(if_freqs, a2_plot)
        lines[1].set_data(if_freqs, b2_plot)
        lines[2].set_data(if_test_freqs[:i+1], np.abs(ab_ratios))
        lines[3].set_data(if_test_freqs[:i+1], np.angle(ab_ratios, deg=True))
        fig.canvas.draw()
        fig.canvas.flush_events()
        
        # save data
        np.savez(cal_datadir+"/rawdata_tone_" + tone_sideband + "/chnl_" + 
        str(chnl), a2=a2, b2=b2, ab_re=ab_re, ab_im=ab_im)

    # compute interpolations
    a2_arr = np.interp(if_freqs, if_test_freqs, a2_arr)
    b2_arr = np.interp(if_freqs, if_test_freqs, b2_arr)
    ab_arr = np.interp(if_freqs, if_test_freqs, ab_arr)

    return a2_arr, b2_arr, ab_arr

def print_data():
    """
    Print the saved data to .pdf images for an easy check.
    """
    # get data
    caldata = np.load(cal_datadir + "/caldata.npz")
    a2_toneusb = caldata['a2_toneusb']; a2_tonelsb = caldata['a2_tonelsb']
    b2_toneusb = caldata['b2_toneusb']; b2_tonelsb = caldata['b2_tonelsb']
    ab_toneusb = caldata['ab_toneusb']; ab_tonelsb = caldata['ab_tonelsb']

    # compute ratios
    ab_ratios_usb = ab_toneusb / b2_toneusb
    ab_ratios_lsb = ab_tonelsb / b2_tonelsb

    # print magnitude ratios
    plt.figure()
    plt.plot(rf_freqs_usb, np.abs(ab_ratios_usb), 'b')
    plt.plot(rf_freqs_lsb, np.abs(ab_ratios_lsb), 'r')
    plt.grid()                 
    plt.xlabel('Frequency [GHz]')
    plt.ylabel('Mag ratio [lineal]')     
    plt.savefig(cal_datadir+'/mag_ratios.pdf')
    
    # print angle difference
    plt.figure()
    plt.plot(rf_freqs_usb, np.angle(ab_ratios_usb, deg=True), 'b')
    plt.plot(rf_freqs_lsb, np.angle(ab_ratios_lsb, deg=True), 'r')
    plt.grid()                 
    plt.xlabel('Frequency [GHz]')
    plt.ylabel('Angle diff [degrees]')     
    plt.savefig(cal_datadir+'/angle_diff.pdf')

def compress_data(datadir):
    """
    Compress the data from the datadir directory into a .tar.gz
    file and delete the original directory.
    :param datair: directory to compress.
    """
    tar = tarfile.open(datadir + ".tar.gz", "w:gz")
    for datafile in os.listdir(datadir):
        tar.add(datadir + '/' + datafile, datafile)
    tar.close()
    shutil.rmtree(datadir)

if __name__ == "__main__":
    main()
