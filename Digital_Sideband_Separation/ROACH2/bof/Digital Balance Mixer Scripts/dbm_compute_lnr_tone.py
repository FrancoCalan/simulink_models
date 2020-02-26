# Script for LNR computation of digital balance mixer. It uses the same
# model as for digital sideband separation. Computes the LO Noise Rejection
# by sweeping a tone thourgh th bandwidth of a calibrated model.
# It then saves the  into a compress folder.

# imports
import os, corr, time, datetime, tarfile, shutil
import numpy as np
import matplotlib.pyplot as plt
import calandigital as cd
from dbm_load_constants import dbm_load_constants

# communication parameters
roach_ip        = '192.168.1.10'
boffile         = 'dss_2048ch_1520mhz.bof.gz'
rf_generator_ip = '192.168.1.31'

# model parameters
adc_bits        = 8
bandwidth       = 1080 # MHz
acc_len_reg     = 'syn_acc_len'
cnt_rst_reg     = 'cnt_rst'
bram_addr_width = 8  # bits
bram_word_width = 64 # bits
pow_data_type   = '>u8'
bram_rf = ['dout0_0', 'dout0_1', 'dout0_2', 'dout0_3', 
           'dout0_4', 'dout0_5', 'dout0_6', 'dout0_7']
bram_lo = ['dout1_0', 'dout1_1', 'dout1_2', 'dout1_3', 
           'dout1_4', 'dout1_5', 'dout1_6', 'dout1_7']

# experiment parameters
lo_freq     = 8000 # MHz
acc_len     = 2**16
chnl_step   = 8
rf_power    = -10 #dBm
date_time   =  datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
datadir     = "bm_lnr_tone " + date_time
pause_time  = 0.5 # should be > (1/bandwidth * FFT_size * acc_len * 2) in order 
                  # for the spectra to be fully computed after a tone change
load_consts = True
load_ideal  = True
caldir      = None

# derivative parameters
nchannels     = 2**bram_addr_width * len(bram_rf)
if_freqs      = np.linspace(0, bandwidth, nchannels, endpoint=False)
test_channels = range(1, nchannels, chnl_step)
if_test_freqs = if_freqs[test_channels]
dBFS          = 6.02*adc_bits + 1.76 + 10*np.log10(nchannels)                

##########################
# Experiment Starts Here #
##########################
def main():
    global roach, rf_generator, fig, line0, line1, line2
    start_time = time.time()

    roach = cd.initialize_roach(roach_ip)
    rf_generator = cd.Instrument(rf_generator_ip)

    print("Setting up plotting and data saving elements...")
    fig, line0, line1, line2 = create_figure()
    make_data_directory()
    print("done")

    #####################
    # Start Measurement #
    #####################
    # loading calibration constants
    if load_consts:
        bm_load_constants(roach, load_ideal, 1+0j, caldir)

    print("Setting and resetting registers...")
    roach.write_int(acc_len_reg, acc_len)
    roach.write_int(cnt_rst_reg, 1)
    roach.write_int(cnt_rst_reg, 0)
    print("done")

    print("Setting instrumets power and outputs...")
    rf_generator.write("power " + str(rf_power))
    rf_generator.write("outp on")
    print("done")

    print("Starting tone sweep in upper sideband...")
    sweep_time = time.time()
    rf_freqs = lo_freq + if_freqs
    rf_usb, lo_usb = get_lnrdata(rf_freqs, "usb")
    print("done (" +str(int(time.time() - sweep_time)) + "[s])")
        
    print("Starting tone sweep in lower sideband...")
    sweep_time = time.time()
    rf_freqs = lo_freq - if_freqs
    rf_lsb, lo_lsb = get_lnrdata(rf_freqs, "lsb")
    print("done (" +str(int(time.time() - sweep_time)) + "[s])")

    print("Turning off intruments...")
    rf_generator.write("outp off")
    print("done")

    print("Saving data...")
    np.savez(datadir+"/lnrdata", 
        rf_usb=rf_usb, lo_usb=lo_usb,
        rf_lsb=rf_lsb, lo_lsb=lo_lsb)
    print("done")

    print("Printing data...")
    print_data()
    print("done")

    print("Compressing data...")
    compress_data()
    print("done")

    print("Finished. Total time: " + str(int(time.time() - start_time)) + "[s]")

def create_figure():
    """
    Creates figure for plotting.
    """
    fig, [[ax0, ax1], [ax2, _]] = plt.subplots(2,2)
    fig.set_tight_layout(True)
    fig.show()
    fig.canvas.draw()
    
    # get line objects
    line0, = ax0.plot([],[])
    line1, = ax1.plot([],[])
    line2, = ax2.plot([],[])
    
    # set spectrometers axes
    ax0.set_xlim((0, bandwidth))     ; ax1.set_xlim((0, bandwidth))
    ax0.set_ylim((-80, 0))           ; ax1.set_ylim((-80, 0))
    ax0.grid()                       ; ax1.grid()
    ax0.set_xlabel('Frequency [MHz]'); ax1.set_xlabel('Frequency [MHz]')
    ax0.set_ylabel('Power [dBFS]')   ; ax1.set_ylabel('Power [dBFS]')
    ax0.set_title("RF spec")         ; ax1.set_title("LO spec")

    # LNR axes
    ax2.set_xlim((0, bandwidth))     
    ax2.set_ylim((0, 80))            
    ax2.grid()                       
    ax2.set_xlabel('Frequency [MHz]')
    ax2.set_ylabel('LNR [dB]') 
    ax2.set_title("LNR")         

    return fig, line0, line1, line2

def make_data_directory():
    """
    Make directory where to save all the lnr data.
    """
    os.mkdir(datadir)

    # make .txt file with test info
    with open(datadir + "/testinfo.txt", "w") as f:
        f.write("roach ip:     " + roach_ip         + "\n")
        f.write("date time:    " + date_time        + "\n")
        f.write("boffile:      " + boffile          + "\n")
        f.write("bandwidth:    " + str(bandwidth)   + "\n")
        f.write("lo freq:      " + str(lo_freq)     + "\n")
        f.write("nchannels:    " + str(nchannels)   + "\n")
        f.write("acc len:      " + str(acc_len)     + "\n")
        f.write("chnl step:    " + str(chnl_step)   + "\n")
        f.write("rf generator: " + rf_generator_ip  + "\n")
        f.write("rf power:     " + str(rf_power)    + "\n")
        f.write("load consts:  " + str(load_consts) + "\n")
        f.write("load ideal:   " + str(load_ideal)  + "\n")
        f.write("caldir:       " + str(caldir))

    # make rawdata folders
    os.mkdir(datadir + "/rawdata_usb")
    os.mkdir(datadir + "/rawdata_lsb")

def get_lnrdata(rf_freqs, sideband):
    """
    Sweep a tone through a sideband and get the lnr data.
    The lnr data is the power of each tone after applying the calibration
    constants (rf), and the negative of the constants (lo).
    The full sprecta measured for each tone is saved to data for debugging
    purposes.
    :param rf_freqs: frequencies of the tones to perform the sweep.
    :param sideband: sideband of the mesurement. Either USB or LSB
    :return: lnr data: rf and lo.
    """
    fig.canvas.set_window_title(sideband.upper() + " Sweep")

    rf_arr = []; lo_arr = []
    for i, chnl in enumerate(test_channels):
        # set test tone
        freq = rf_freqs[chnl]
        rf_generator.ask("freq " + str(freq*1e6) + ";*opc?") # freq must be in Hz
        time.sleep(pause_time)

        # read data
        rf = read_interleave_data(roach, bram_rf,  bram_addr_width, 
                                  bram_word_width, pow_data_type)
        lo = read_interleave_data(roach, bram_lo,  bram_addr_width, 
                                  bram_word_width, pow_data_type)

        # append data to arrays
        rf_arr.append(rf[chnl])
        lo_arr.append(lo[chnl])

        # scale and dBFS data for plotting
        rf_plot = cd.scale_and_dBFS_specdata(rf, acc_len, dBFS)
        lo_plot = cd.scale_and_dBFS_specdata(lo, acc_len, dBFS)

        # compute lnr for plotting
        lnr = np.divide(lo_arr, rf_arr)

        # plot data
        line0.set_data(if_freqs, rf_plot)
        line1.set_data(if_freqs, lo_plot)
        line2.set_data(if_test_freqs[:i+1], 10*np.log10(lnr))
        fig.canvas.draw()
        fig.canvas.flush_events()
        
        # save data
        np.savez(datadir+"/rawdata_" + sideband + "/chnl_" + str(chnl), 
            rf=rf, lo=lo)

    # compute interpolations
    rf_arr = np.interp(if_freqs, if_test_freqs, rf_arr)
    lo_arr = np.interp(if_freqs, if_test_freqs, lo_arr)

    return rf_arr, lo_arr

def print_data():
    """
    Print the saved data to .pdf images for an easy check.
    """
    # get rf frequencies
    rf_freqs_usb = lo_freq + if_freqs
    rf_freqs_lsb = lo_freq - if_freqs

    # get data
    lnrdata = np.load(datadir + "/lnrdata.npz")
    rf_usb = lnrdata['rf_usb']; rf_lsb = lnrdata['rf_lsb']
    lo_usb = lnrdata['lo_usb']; lo_lsb = lnrdata['lo_lsb']

    # compute ratios
    lnr_usb = lo_usb / rf_usb
    lnr_lsb = lo_lsb / rf_lsb

    # print LNR
    plt.figure()
    plt.plot(rf_freqs_usb, 10*np.log10(lnr_usb), 'b')
    plt.plot(rf_freqs_lsb, 10*np.log10(lnr_lsb), 'b')
    plt.grid()                 
    plt.xlabel('Frequency [MHz]')
    plt.ylabel('LNR [dB]')     
    plt.savefig(datadir+'/lnr.pdf')
    
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
