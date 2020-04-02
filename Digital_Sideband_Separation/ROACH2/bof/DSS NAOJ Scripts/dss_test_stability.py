#!/usr/bin/python
# Script for tone calibration of digital sideband separating receiver with 
# multiple LO values and multiple LO stages.

# imports
import os, time, tarfile, shutil, json
import numpy as np
import matplotlib.pyplot as plt
import calandigital as cd
from dss_load_constants import dss_load_constants
from dss_multilo_parameters import *

def main():
    start_time = time.time()

    make_pre_measurements_actions()
    make_dss_stability_measurements()

def make_pre_measurements_actions():
    """
    Makes all the actions in preparation for the measurements:
    - initizalize ROACH and generator communications.
    - creating plotting and data saving elements
    - setting initial registers in FPGA
    - turning on generator power
    """
    global roach, rf_generator, lo1_generator, lo2_generator, fig, lines, axes

    roach = cd.initialize_roach(roach_ip)
    lo1_generator = rm.open_resource(lo1_generator_name)
    lo2_generator = rm.open_resource(lo2_generator_name)
    rf_generator  = rm.open_resource(rf_generator_name)

    print("Setting up plotting and data saving elements...")
    if show_plots:
        fig, lines, axes = create_figure()
    #make_data_directory()
    print("done")

    print("Setting accumulation register to " + str(acc_len) + "...")
    roach.write_int(cal_acc_len_reg, acc_len)
    print("done")
    print("Resseting counter registers...")
    roach.write_int(cnt_rst_reg, 1)
    roach.write_int(cnt_rst_reg, 0)
    print("done")
    
    print("Setting instruments power and outputs...")
    lo1_generator.write("power " + str(lo1_power))
    lo1_generator.write("freq:mult " + str(lo1_mult))
    lo2_generator.write("power " + str(lo2_power))
    rf_generator.write("power " + str(rf_power))
    rf_generator.write("freq:mult " + str(rf_mult))
    lo1_generator.write("outp on")
    lo2_generator.write("outp on")
    rf_generator.write("outp on")
    print("done")

def make_dss_stability_measurements():
    lo1_freq = lo1_freqs[0]
    lo2_freq = lo2_freqs[0]
    lo1_generator.ask("freq " + str(lo1_freq) + " ghz; *opc?")
    lo2_generator.ask("freq " + str(lo2_freq) + "ghz; *opc?")

    # compute rf frequencies
    rf_freqs_usb = lo1_freq + lo2_freq + (if_freqs/1e3) # GHz
    rf_freqs_lsb = lo1_freq - lo2_freq - (if_freqs/1e3) # GHz

    freq = rf_freqs_usb[stab_chnl]
    rf_generator.ask("freq " + str(freq) + " ghz; *opc?")
    time.sleep(pause_time)

    # load constants
    measname = "lo1_" + str(lo1_freq) + "ghz_lo2_" + \
                        str(lo2_freq) + "ghz"
    print("Extracting compressed calibration data...")
    caldir = caltar[:-7]
    tarfile.open(caltar).extractall(path=caldir)
    print("done.")
    dss_load_constants(roach, caldir + "/" + measname)
    shutil.rmtree(caldir)

    # plot stability data
    plot_stability_data()

def make_post_measurements_actions():
    """
    Makes all the actions required after measurements:
    - turn off sources
    - compress data
    - write calibration data name in file
    """
    print("Turning off instruments...")
    #lo1_generator.write("freq:mult 1")
    #rf_generator.write("freq:mult 1")
    lo1_generator.write("outp off")
    lo2_generator.write("outp off")
    rf_generator.write("outp off")
    rm.close()
    print("done")

    make_data_directory()
    np.savez(stab_datadir+"/stabdata", 
        a2_arr=a2_arr,
        b2_arr=b2_arr,
        anglediff_arr=anglediff_arr,
        magratios_arr=magratios_arr,
        srr_arr=srr_arr,
        time_arr=time_arr)

    print("Compressing data...")
    compress_data(stab_datadir)
    print("done")

def create_figure():
    """
    Creates figure for plotting.
    """
    fig, [ax0, ax1, ax2, ax3, ax4] = plt.subplots(5,1, sharex=True)
    fig.set_tight_layout(True)
    fig.show()
    fig.canvas.draw()
    
    # get line objects
    line0, = ax0.plot([],[])
    line1, = ax1.plot([],[])
    line2, = ax2.plot([],[])
    line3, = ax3.plot([],[])
    line4, = ax4.plot([],[])
    lines  = [line0, line1, line2, line3, line4] 
    
    # set spectrometers axes
    ax0.grid()                       
    ax1.grid()                       
    ax2.grid()                       
    ax3.grid()                       
    ax4.grid()                       
    ax0.set_ylabel('USB [dBFS]')
    ax1.set_ylabel('LSB [dBFS]')
    ax2.set_ylabel('mag ratio [l]')
    ax3.set_ylabel('ang diff [d]')
    ax4.set_ylabel('SRR [dB]')
    ax4.set_xlabel('Time [s]')
    ax1.yaxis.set_label_position("right")
    ax1.yaxis.tick_right()
    ax3.yaxis.set_label_position("right")
    ax3.yaxis.tick_right()

    return fig, lines, [ax0, ax1, ax2, ax3, ax4]

def make_data_directory():
    """
    Make directory where to save all the calibration data.
    """
    os.mkdir(stab_datadir)

    # make .json file with test info
    testinfo = {}
    testinfo["roach ip"]           = roach_ip
    testinfo["date time"]          = date_time
    testinfo["boffile"]            = boffile
    testinfo["bandwidth mhz"]      = bandwidth
    testinfo["nchannels"]          = nchannels
    testinfo["acc len"]            = acc_len
    testinfo["lo1 generator name"] = lo1_generator_name
    testinfo["lo2 generator name"] = lo2_generator_name
    testinfo["lo1 freqs ghz"]      = str(lo1_freqs)
    testinfo["lo2 freqs ghz"]      = str(lo2_freqs)
    testinfo["lo1 power dbm"]      = lo1_power
    testinfo["lo2 power dbm"]      = lo2_power
    testinfo["rf generator name"]  = rf_generator_name
    testinfo["rf power dbm"]       = rf_power
    testinfo["stab chnl"]          = stab_chnl

    with open(stab_datadir + "/testinfo.json", "w") as f:
        json.dump(testinfo, f, indent=4, sort_keys=True)


def plot_stability_data():
    global a2_arr, b2_arr, anglediff_arr, magratios_arr, srr_arr, time_arr

    tone_sideband = 'usb'
    a2_arr = []; b2_arr = []; 
    magratios_arr = []; anglediff_arr = [];  
    srr_arr = []; time_arr = []
    start_time = time.time()
    
    try:
        while True:
            time.sleep(pause_time)
            time_arr.append(time.time()- start_time)
            # read cal data
            a2    = cd.read_interleave_data(roach, bram_a2,    bram_addr_width, 
                                            bram_word_width,   pow_data_type)
            b2    = cd.read_interleave_data(roach, bram_b2,    bram_addr_width, 
                                            bram_word_width,   pow_data_type)
            ab_re = cd.read_interleave_data(roach, bram_ab_re, bram_addr_width, 
                                            bram_word_width,   crosspow_data_type)
            ab_im = cd.read_interleave_data(roach, bram_ab_im, bram_addr_width, 
                                            bram_word_width,   crosspow_data_type)
            
            # read syn data
            usb = cd.read_interleave_data(roach, bram_usb, bram_addr_width, 
                                          bram_word_width, pow_data_type)
            lsb = cd.read_interleave_data(roach, bram_lsb, bram_addr_width, 
                                          bram_word_width, pow_data_type)

            # scale and dBFS data for plotting
            a2_plot = cd.scale_and_dBFS_specdata(a2, acc_len, dBFS)
            b2_plot = cd.scale_and_dBFS_specdata(b2, acc_len, dBFS)

            ab = ab_re[stab_chnl] + 1j*ab_im[stab_chnl]

            # compute input ratios for plotting
            if tone_sideband=='usb':
                ab_ratio = np.divide(np.conj(ab), a2) # (ab*)* /aa* = a*b / aa* = b/a
            else: # tone_sideband=='lsb
                ab_ratio = np.divide(ab, b2) # ab* / bb* = a/b

            # append data to arrays
            a2_arr.append(a2_plot[stab_chnl])
            b2_arr.append(b2_plot[stab_chnl])
            magratios_arr.append(np.abs(ab_ratio[stab_chnl]))
            anglediff_arr.append(np.angle(ab_ratio[stab_chnl], deg=True))

            # compute srr
            if tone_sideband=='usb':
                srr = np.divide(usb, lsb)
            else: # tone_sideband=='lsb
                srr = np.divide(lsb, usb)

            srr_arr.append(10*np.log10(srr[stab_chnl]))

            # plot data
            if show_plots:
                lines[0].set_data(time_arr, a2_arr)
                lines[1].set_data(time_arr, b2_arr)
                lines[2].set_data(time_arr, magratios_arr)
                lines[3].set_data(time_arr, anglediff_arr)
                lines[4].set_data(time_arr, srr_arr)
                
                # update axes
                axes[0].set_ylim(np.min(a2_arr), np.max(a2_arr))
                axes[1].set_ylim(np.min(b2_arr), np.max(b2_arr))
                axes[2].set_ylim(np.min(magratios_arr), np.max(magratios_arr))
                axes[3].set_ylim(np.min(anglediff_arr), np.max(anglediff_arr))
                axes[4].set_ylim(np.min(srr_arr), np.max(srr_arr))
                axes[4].set_xlim(0, time_arr[-1])

                fig.canvas.draw()
                fig.canvas.flush_events()

    except:
        make_post_measurements_actions()
        
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

if __name__ == '__main__':
    main()
