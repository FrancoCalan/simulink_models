#!/usr/bin/python
# Script for SRR computation of digital sideband separating receiver. Computes 
# the Sideband Rejection Ratio by sweeping a tone through the bandwidth of a 
# calibrated model.
# It then saves the results into a compress folder.

# imports
import os, corr, time, datetime, tarfile, shutil, json
import numpy as np
import matplotlib.pyplot as plt
import calandigital as cd
from dss_load_constants import dss_load_constants

# communication parameters
roach_ip        = '133.40.220.2'
boffile         = 'dss_2048ch_1520mhz.bof.gz'
rf_generator_ip = None

# model parameters
adc_bits        = 8
bandwidth       = 1080 # MHz
acc_len_reg     = 'syn_acc_len'
cnt_rst_reg     = 'cnt_rst'
bram_addr_width = 8  # bits
bram_word_width = 64 # bits
pow_data_type   = '>u8'
bram_usb = ['dout0_0', 'dout0_1', 'dout0_2', 'dout0_3', 
            'dout0_4', 'dout0_5', 'dout0_6', 'dout0_7']
bram_lsb = ['dout1_0', 'dout1_1', 'dout1_2', 'dout1_3', 
            'dout1_4', 'dout1_5', 'dout1_6', 'dout1_7']

# experiment parameters
lo_freq     = 3000 # MHz
rf_power    = -50 # dBm
acc_len     = 2**16
chnl_step   = 32
date_time   =  datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
datadir     = "dss_srr " + date_time
pause_time  = 0.5 # should be > (1/bandwidth * FFT_size * acc_len * 2) in order 
                  # for the spectra to be fully computed after a tone change
load_consts = True
load_ideal  = False
caldir      = 'dss_cal 2020-03-16 10:36:22.tar.gz'

# derivative parameters
nchannels     = 2**bram_addr_width * len(bram_lsb)
if_freqs      = np.linspace(0, bandwidth, nchannels, endpoint=False) # MHz
test_channels = range(1, nchannels, chnl_step)
if_test_freqs = if_freqs[test_channels] # MHz
rf_freqs_usb  = lo_freq + if_freqs # MHz
rf_freqs_lsb  = lo_freq - if_freqs # MHz
dBFS          = 6.02*adc_bits + 1.76 + 10*np.log10(nchannels)                

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
    start_time = time.time()

    roach = cd.initialize_roach(roach_ip)
    rf_generator = cd.Instrument(rf_generator_ip)

    print("Setting up plotting and data saving elements...")
    fig, lines = create_figure()
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
    rf_generator.write("power " + str(rf_power))
    rf_generator.write("outp on")
    print("done")

def make_dss_measurements():
    """
    Makes the measurements for dss calibration.
    """
    # loading calibration constants
    if load_consts:
        dss_load_constants(roach, load_ideal, 0-1j, caldir)

    print("Starting tone sweep in upper sideband...")
    sweep_time = time.time()
    usb_toneusb, lsb_toneusb = get_srrdata(rf_freqs_usb, "usb")
    print("done (" +str(int(time.time() - sweep_time)) + "[s])")
        
    print("Starting tone sweep in lower sideband...")
    sweep_time = time.time()
    usb_tonelsb, lsb_tonelsb = get_srrdata(rf_freqs_lsb, "lsb")
    print("done (" +str(int(time.time() - sweep_time)) + "[s])")

    print("Saving data...")
    np.savez(datadir+"/srrdata", 
        usb_toneusb=usb_toneusb, lsb_toneusb=lsb_toneusb,
        usb_tonelsb=usb_tonelsb, lsb_tonelsb=lsb_tonelsb)
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
    compress_data()
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
    ax0.set_ylim((-80, 5))           ; ax1.set_ylim((-80, 5))
    ax0.grid()                       ; ax1.grid()
    ax0.set_xlabel('Frequency [MHz]'); ax1.set_xlabel('Frequency [MHz]')
    ax0.set_ylabel('Power [dBFS]')   ; ax1.set_ylabel('Power [dBFS]')
    ax0.set_title('USB spec')        ; ax1.set_title('LSB spec')

    # SRR axes
    ax2.set_xlim((0, bandwidth))     ; ax3.set_xlim((0, bandwidth))     
    ax2.set_ylim((0, 80))            ; ax3.set_ylim((0, 80))            
    ax2.grid()                       ; ax3.grid()                       
    ax2.set_xlabel('Frequency [MHz]'); ax3.set_xlabel('Frequency [MHz]')
    ax2.set_ylabel('SRR [dB]')       ; ax3.set_ylabel('SRR [dB]') 
    ax2.set_title('SRR USB')         ; ax3.set_title('SRR LSB')         

    return fig, lines

def make_data_directory():
    """
    Make directory where to save all the srr data.
    """
    os.mkdir(datadir)

    # make .json file with test info
    testinfo = {}
    testinfo["roach ip"]        = roach_ip
    testinfo["date time"]       = date_time
    testinfo["boffile"]         = boffile
    testinfo["bandwidth mhz"    = bandwidth
    testinfo["lo freq"]         = lo_freq
    testinfo["nchannels"]       = nchannels
    testinfo["acc len"]         = acc_len
    testinfo["chnl step"]       = chnl_step
    testinfo["rf generator ip"] = rf_generator_ip
    testinfo["rf power dbm"]    = rf_power
    testinfo["load consts"]     = load_consts
    testinfo["load ideal"]      = load_ideal
    testinfo["caldir"]          = caldir

    with open(datadir + "/testinfo.json", "w") as f:
        json.dump(testinfo, f, indent=4, sort_keys=True)

    # make rawdata folders
    os.mkdir(datadir + "/rawdata_tone_usb")
    os.mkdir(datadir + "/rawdata_tone_lsb")

def get_srrdata(rf_freqs, tone_sideband):
    """
    Sweep a tone through a sideband and get the srr data.
    The srr data is the power of each tone after applying the calibration
    constants for each sideband (usb and lsb).
    The full sprecta measured for each tone is saved to data for debugging
    purposes.
    :param rf_freqs: frequencies of the tones to perform the sweep.
    :param tone_sideband: sideband of the injected test tone. Either USB or LSB
    :return: srr data: usb and lsb.
    """
    fig.canvas.set_window_title(tone_sideband.upper() + " Tone Sweep")

    usb_arr = []; lsb_arr = []
    for i, chnl in enumerate(test_channels):
        # set test tone
        freq = rf_freqs[chnl]
        rf_generator.ask("freq " + str(freq*1e6) + ";*opc?") # freq must be in Hz
        time.sleep(pause_time)

        # read data
        usb = cd.read_interleave_data(roach, bram_usb, bram_addr_width, 
                                      bram_word_width, pow_data_type)
        lsb = cd.read_interleave_data(roach, bram_lsb, bram_addr_width, 
                                      bram_word_width, pow_data_type)

        # append data to arrays
        usb_arr.append(usb[chnl])
        lsb_arr.append(lsb[chnl])

        # scale and dBFS data for plotting
        usb_plot = cd.scale_and_dBFS_specdata(usb, acc_len, dBFS)
        lsb_plot = cd.scale_and_dBFS_specdata(lsb, acc_len, dBFS)

        # compute srr for plotting
        if tone_sideband=='usb':
            srr = np.divide(usb_arr, lsb_arr)
        else: # tone_sideband=='lsb
            srr = np.divide(lsb_arr, usb_arr)

        # define sb plot line
        line_sb = lines[2] if tone_sideband=='usb' else lines[3]

        # plot data
        lines[0].set_data(if_freqs, usb_plot)
        lines[1].set_data(if_freqs, lsb_plot)
        line_sb.set_data(if_test_freqs[:i+1], 10*np.log10(srr))
        fig.canvas.draw()
        fig.canvas.flush_events()
        
        # save data
        np.savez(datadir+"/rawdata_tone_" + tone_sideband + "/chnl_" + str(chnl), 
            usb=usb, lsb=lsb)

    # compute interpolations
    usb_arr = np.interp(if_freqs, if_test_freqs, usb_arr)
    lsb_arr = np.interp(if_freqs, if_test_freqs, lsb_arr)

    return usb_arr, lsb_arr

def print_data():
    """
    Print the saved data to .pdf images for an easy check.
    """
    # get data
    srrdata = np.load(datadir + "/srrdata.npz")
    usb_toneusb = srrdata['usb_toneusb']; lsb_toneusb = srrdata['lsb_toneusb']
    usb_tonelsb = srrdata['usb_tonelsb']; lsb_tonelsb = srrdata['lsb_tonelsb']

    # compute ratios
    srr_usb = usb_toneusb / lsb_toneusb
    srr_lsb = lsb_tonelsb / usb_tonelsb

    # print SRR
    plt.figure()
    plt.plot(rf_freqs_usb, 10*np.log10(srr_usb), 'b')
    plt.plot(rf_freqs_lsb, 10*np.log10(srr_lsb), 'r')
    plt.grid()                 
    plt.xlabel('Frequency [MHz]')
    plt.ylabel('SRR [dB]')     
    plt.savefig(datadir+'/srr.pdf')
    
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

if __name__ == "__main__":
    main()
