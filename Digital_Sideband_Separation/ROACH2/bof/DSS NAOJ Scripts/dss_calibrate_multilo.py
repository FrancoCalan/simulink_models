#!/usr/bin/python
# Script for tone calibration of digital sideband separating receiver with 
# multiple LO values and multiple LO stages.

# imports
import os, time, tarfile, shutil, json
import numpy as np
import matplotlib.pyplot as plt
import calandigital as cd
from dss_multilo_parameters import *

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
    global roach, rf_generator, lo1_generator, lo2_generator, fig, lines

    roach = cd.initialize_roach(roach_ip)
    lo1_generator = rm.open_resource(lo1_generator_name)
    lo2_generator = rm.open_resource(lo2_generator_name)
    rf_generator  = rm.open_resource(rf_generator_name)

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
    lo1_generator.write("power " + str(lo1_power))
    lo1_generator.write("freq:mult " + str(lo1_mult))
    lo2_generator.write("power " + str(lo2_power))
    rf_generator.write("power " + str(rf_power))
    rf_generator.write("freq:mult " + str(rf_mult))
    lo1_generator.write("outp on")
    lo2_generator.write("outp on")
    rf_generator.write("outp on")
    print("done")

def make_dss_multilo_measurements():
    """
    Makes the measurements for dss calibration with multiple LOs.
    :param datair: directory where to save the data.
    """
    for lo1_freq in lo1_freqs:
        # set lo1 frequency
        lo1_generator.ask("freq " + str(lo1_freq) + " ghz; *opc?")
        
        for lo2_freq in lo2_freqs:
            # set lo2 frequency
            lo2_generator.ask("freq " + str(lo2_freq) + "ghz; *opc?")

            # print setting
            print("Current LOs: LO1:" + str(lo1_freq) + "GHz," +
                              " LO2:" + str(lo2_freq) + "GHz")
            
            # make measurement subdirectory
            measname = "lo1_" + str(lo1_freq) + "ghz_lo2_" + \
                                str(lo2_freq) + "ghz"
            measdir = cal_datadir + "/" + measname
            os.mkdir(measdir)
            os.mkdir(measdir + "/rawdata_tone_usb")
            os.mkdir(measdir + "/rawdata_tone_lsb")
            
            # compute rf frequencies
            rf_freqs_usb = lo1_freq + lo2_freq + (if_freqs/1e3) # GHz
            rf_freqs_lsb = lo1_freq - lo2_freq - (if_freqs/1e3) # GHz

            # make measurement
            make_dss_measurements(measdir, rf_freqs_usb, rf_freqs_lsb)

    print_multilo_data()

def make_post_measurements_actions():
    """
    Makes all the actions required after measurements:
    - turn off sources
    - compress data
    """
    print("Turning off instruments...")
    lo1_generator.write("freq:mult 1")
    rf_generator.write("freq:mult 1")
    lo1_generator.write("outp off")
    lo2_generator.write("outp off")
    rf_generator.write("outp off")
    rm.close()
    print("done")

    print("Compressing data...")
    compress_data(cal_datadir)
    print("done")

    # Write file to save last calibration directory
    f = open("last_caltar.txt", "w"); f.write(cal_datadir+".tar.gz"); f.close();

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
    ax2.set_ylim((0, 1))     
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
    testinfo["roach ip"]           = roach_ip
    testinfo["date time"]          = date_time
    testinfo["boffile"]            = boffile
    testinfo["bandwidth mhz"]      = bandwidth
    testinfo["nchannels"]          = nchannels
    testinfo["acc len"]            = acc_len
    testinfo["chnl step"]          = chnl_step
    testinfo["lo1 generator name"] = lo1_generator_name
    testinfo["lo2 generator name"] = lo2_generator_name
    testinfo["lo1 freqs ghz"]      = str(lo1_freqs)
    testinfo["lo2 freqs ghz"]      = str(lo2_freqs)
    testinfo["lo1 power dbm"]      = lo1_power
    testinfo["lo2 power dbm"]      = lo2_power
    testinfo["rf generator name"]  = rf_generator_name
    testinfo["rf power dbm"]       = rf_power

    with open(cal_datadir + "/testinfo.json", "w") as f:
        json.dump(testinfo, f, indent=4, sort_keys=True)

def make_dss_measurements(measdir, rf_freqs_usb, rf_freqs_lsb):
    """
    Makes the measurements for dss calibration for a single set of LOs.
    :param measdir: directory where to save the data of this measurement
        (sub directory of main cal_datadir).
    :param rf_freqs_usb: rf frequencies to measure in usb (GHz).
    :param rf_freqs_lsb: rf frequencies to measure in lsb (GHz).
    """
    print("Starting tone sweep in upper sideband...")
    sweep_time = time.time()
    a2_toneusb, b2_toneusb, ab_toneusb = get_caldata(measdir, rf_freqs_usb, "usb")
    print("done (" +str(int(time.time() - sweep_time)) + "[s])")
        
    print("Starting tone sweep in lower sideband...")
    sweep_time = time.time()
    a2_tonelsb, b2_tonelsb, ab_tonelsb = get_caldata(measdir, rf_freqs_lsb, "lsb")
    print("done (" +str(int(time.time() - sweep_time)) + "[s])")

    print("Saving data...")
    np.savez(measdir+"/caldata", 
        a2_toneusb=a2_toneusb, b2_toneusb=b2_toneusb, ab_toneusb=ab_toneusb,
        a2_tonelsb=a2_tonelsb, b2_tonelsb=b2_tonelsb, ab_tonelsb=ab_tonelsb)
    print("done")

    print("Printing data...")
    print_singlelo_data(measdir)
    print("done")

def get_caldata(measdir, rf_freqs, tone_sideband):
    """
    Sweep a tone through a sideband and get the calibration data.
    The calibration data is the power of each tone in both inputs (a and b)
    and the cross-correlation of both inputs as a complex number (ab*).
    The full sprecta measured for each tone is saved to data for debugging
    purposes.
    :param measdir: directory where to save the raw data.
    :param rf_freqs: frequencies of the tones to perform the sweep (GHz).
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
        if tone_sideband=='usb':
            ab_ratios = np.divide(np.conj(ab_arr), a2_arr) # (ab*)* /aa* = a*b / aa* = b/a
        else: # tone_sideband=='lsb
            ab_ratios = np.divide(ab_arr, b2_arr) # ab* / bb* = a/b

        # plot data
        lines[0].set_data(if_freqs, a2_plot)
        lines[1].set_data(if_freqs, b2_plot)
        lines[2].set_data(if_test_freqs[:i+1], np.abs(ab_ratios))
        lines[3].set_data(if_test_freqs[:i+1], np.angle(ab_ratios, deg=True))
        fig.canvas.draw()
        fig.canvas.flush_events()
        
        # save data
        rawdata_dir = measdir+"/rawdata_tone_" + tone_sideband
        np.savez(rawdata_dir + "/chnl_" + str(chnl), 
            a2=a2, b2=b2, ab_re=ab_re, ab_im=ab_im)

        # print raw spectral data
        print_spec_data(rawdata_dir, chnl)

    # compute interpolations
    a2_arr = np.interp(if_freqs, if_test_freqs, a2_arr)
    b2_arr = np.interp(if_freqs, if_test_freqs, b2_arr)
    ab_arr = np.interp(if_freqs, if_test_freqs, ab_arr)

    return a2_arr, b2_arr, ab_arr

def print_spec_data(rawdata_dir, chnl):
    """
    Print the saved data to .pdf images for an easy check.
    :param rawdata_dir: directory where to read the data and print the plot.
    :param chnl: channel where the tone is injected.
    """
    # get data
    specdata = np.load(rawdata_dir + "/chnl_" + str(chnl) + ".npz")
    a2 = specdata['a2']
    b2 = specdata['b2']

    # compute power levels
    pow_a2 = cd.scale_and_dBFS_specdata(a2, acc_len, dBFS)
    pow_b2 = cd.scale_and_dBFS_specdata(b2, acc_len, dBFS)

    # plot spec usb
    plt.figure()
    plt.plot(if_freqs, pow_a2, 'b')
    plt.ylim((-85, 5))
    plt.grid()                 
    plt.xlabel('Frequency [MHz]')
    plt.ylabel('Power [dBFS]')     
    plt.savefig(rawdata_dir+'/chnl_' + str(chnl) + '_a2.pdf')
    plt.close()

    # plot spec lsb
    plt.figure()
    plt.plot(if_freqs, pow_b2, 'r')
    plt.ylim((-85, 5))
    plt.grid()                 
    plt.xlabel('Frequency [MHz]')
    plt.ylabel('Power [dBFS]')     
    plt.savefig(rawdata_dir+'/chnl_' + str(chnl) + '_b2.pdf')
    plt.close()

def print_singlelo_data(measdir):
    """
    Print the saved data to .pdf images for an easy check.
    :param measdir: directory where to read the data of single measurement
    and save the image (sub directory of main cal_datadir).
    """
    # get data
    caldata = np.load(measdir + "/caldata.npz")
    a2_toneusb = caldata['a2_toneusb']; a2_tonelsb = caldata['a2_tonelsb']
    b2_toneusb = caldata['b2_toneusb']; b2_tonelsb = caldata['b2_tonelsb']
    ab_toneusb = caldata['ab_toneusb']; ab_tonelsb = caldata['ab_tonelsb']

    # compute power levels
    pow_a2_toneusb = cd.scale_and_dBFS_specdata(a2_toneusb, acc_len, dBFS)
    pow_a2_tonelsb = cd.scale_and_dBFS_specdata(a2_tonelsb, acc_len, dBFS)
    pow_b2_toneusb = cd.scale_and_dBFS_specdata(b2_toneusb, acc_len, dBFS)
    pow_b2_tonelsb = cd.scale_and_dBFS_specdata(b2_tonelsb, acc_len, dBFS)

    # compute ratios
    ab_ratios_usb = np.conj(ab_toneusb) / a2_toneusb # (ab*)* /aa* = a*b / aa* = b/a
    ab_ratios_lsb = ab_tonelsb / b2_tonelsb # ab* / bb* = a/b
    
    # compute srr analog
    srr_usb = a2_toneusb / b2_toneusb
    srr_lsb = b2_tonelsb / a2_tonelsb

    # print power level signal
    plt.figure()
    plt.plot(if_freqs, pow_a2_toneusb, 'b', label="USB toneUSB")
    plt.plot(if_freqs, pow_b2_tonelsb, 'r', label="LSB toneLSB")
    plt.grid()                 
    plt.xlabel('Frequency [MHz]')
    plt.ylabel('Power [dBFS]')
    plt.legend()
    plt.savefig(measdir+'/power_lev_sig.pdf')
    plt.close()
    
    # print power level image
    plt.figure()
    plt.plot(if_freqs, pow_a2_tonelsb, 'b', label="USB toneLSB")
    plt.plot(if_freqs, pow_b2_toneusb, 'r', label="LSB toneUSB")
    plt.grid()                 
    plt.xlabel('Frequency [MHz]')
    plt.ylabel('Power [dBFS]')
    plt.legend()
    plt.savefig(measdir+'/power_lev_img.pdf')
    plt.close()
    
    # print magnitude ratios
    plt.figure()
    plt.plot(if_freqs, np.abs(ab_ratios_usb), 'b', label="USB")
    plt.plot(if_freqs, np.abs(ab_ratios_lsb), 'r', label="LSB")
    plt.grid()                 
    plt.xlabel('Frequency [MHz]')
    plt.ylabel('Mag ratio [lineal]')     
    plt.legend()
    plt.savefig(measdir+'/mag_ratios.pdf')
    plt.close()
    
    # print angle difference
    plt.figure()
    plt.plot(if_freqs, np.angle(ab_ratios_usb, deg=True), 'b', label="USB")
    plt.plot(if_freqs, np.angle(ab_ratios_lsb, deg=True), 'r', label="LSB")
    plt.grid()                 
    plt.xlabel('Frequency [MHz]')
    plt.ylabel('Angle diff [degrees]')     
    plt.legend()
    plt.savefig(measdir+'/angle_diff.pdf')
    plt.close()

    # print srr analog
    plt.figure()
    plt.plot(if_freqs, 10*np.log10(srr_usb), 'b', label="USB")
    plt.plot(if_freqs, 10*np.log10(srr_lsb), 'r', label="LSB")
    plt.grid()                 
    plt.xlabel('Frequency [MHz]')
    plt.ylabel('SRR [dB]')     
    plt.legend()
    plt.savefig(measdir+'/srr_analog.pdf')
    plt.close()

def print_multilo_data():
    """
    Print the saved data from all LO settings to .pdf image.
    """
    # create power level signal figure 
    fig1, ax1 = plt.subplots(1,1)
    ax1.grid()                 
    ax1.set_xlabel('Frequency [GHz]')
    ax1.set_ylabel('Power [dBFS]')
    
    # create power level image figure 
    fig2, ax2 = plt.subplots(1,1)
    ax2.grid()                 
    ax2.set_xlabel('Frequency [GHz]')
    ax2.set_ylabel('Power [dBFS]')
    
    # create magnitude ratio figure
    fig3, ax3 = plt.subplots(1,1)
    ax3.grid()                 
    ax3.set_xlabel('Frequency [GHz]')
    ax3.set_ylabel('Mag ratio [lineal]')     

    # create angle difference figure
    fig4, ax4 = plt.subplots(1,1)
    ax4.grid()                 
    ax4.set_xlabel('Frequency [GHz]')
    ax4.set_ylabel('Angle diff [degrees]')     

    # create analog srr figure
    fig5, ax5 = plt.subplots(1,1)
    ax5.grid()                 
    ax5.set_xlabel('Frequency [GHz]')
    ax5.set_ylabel('SRR [dB]')     

    # get colors for plotting
    colors = plt.rcParams['axes.prop_cycle'].by_key()['color']

    for lo1_freq, color in zip(lo1_freqs, colors):
        for lo2_freq in lo2_freqs:
            # get measurement subdirectory
            measname = "lo1_" + str(lo1_freq) + "ghz_lo2_" + \
                                str(lo2_freq) + "ghz"
            measdir = cal_datadir + "/" + measname
            
            # compute rf frequencies
            rf_freqs_usb = lo1_freq + lo2_freq + (if_freqs/1e3) # GHz
            rf_freqs_lsb = lo1_freq - lo2_freq - (if_freqs/1e3) # GHz

            # get data
            caldata = np.load(measdir + "/caldata.npz")
            a2_toneusb = caldata['a2_toneusb']
            a2_tonelsb = caldata['a2_tonelsb']
            b2_toneusb = caldata['b2_toneusb']
            b2_tonelsb = caldata['b2_tonelsb']
            ab_toneusb = caldata['ab_toneusb']
            ab_tonelsb = caldata['ab_tonelsb']
        
            # compute power levels
            pow_a2_toneusb = cd.scale_and_dBFS_specdata(a2_toneusb, acc_len, dBFS)
            pow_a2_tonelsb = cd.scale_and_dBFS_specdata(a2_tonelsb, acc_len, dBFS)
            pow_b2_toneusb = cd.scale_and_dBFS_specdata(b2_toneusb, acc_len, dBFS)
            pow_b2_tonelsb = cd.scale_and_dBFS_specdata(b2_tonelsb, acc_len, dBFS)

            # plot power levels signal
            ax1.plot(rf_freqs_usb, pow_a2_toneusb, color=color)
            ax1.plot(rf_freqs_lsb, pow_b2_tonelsb, color=color)
            
            # plot power levels image
            ax2.plot(rf_freqs_usb, pow_a2_tonelsb, color=color)
            ax2.plot(rf_freqs_lsb, pow_b2_toneusb, color=color)

            # compute ratios
            ab_ratios_usb = np.conj(ab_toneusb) / a2_toneusb # (ab*)* /aa* = a*b / aa* = b/a
            ab_ratios_lsb = ab_tonelsb / b2_tonelsb # ab* / bb* = a/b
            
            # plot magnitude ratios
            ax3.plot(rf_freqs_usb, np.abs(ab_ratios_usb), color=color)
            ax3.plot(rf_freqs_lsb, np.abs(ab_ratios_lsb), color=color)
            
            # plot angle difference
            ax4.plot(rf_freqs_usb, np.angle(ab_ratios_usb, deg=True), color=color)
            ax4.plot(rf_freqs_lsb, np.angle(ab_ratios_lsb, deg=True), color=color)
    
            # compute srr analog
            srr_usb = a2_toneusb / b2_toneusb
            srr_lsb = b2_tonelsb / a2_tonelsb
            
            # plot srr analog
            plt.plot(rf_freqs_usb, 10*np.log10(srr_usb), color=color)
            plt.plot(rf_freqs_lsb, 10*np.log10(srr_lsb), color=color)

    # print figures
    fig1.savefig(cal_datadir+'/power_lev_sig.pdf')
    fig2.savefig(cal_datadir+'/power_lev_img.pdf')
    fig3.savefig(cal_datadir+'/mag_ratios.pdf')
    fig4.savefig(cal_datadir+'/angle_diff.pdf')
    fig5.savefig(cal_datadir+'/srr_analog.pdf')

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
