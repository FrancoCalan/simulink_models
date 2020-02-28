# Script for LNR computation of digital balance mixer. It uses the same
# model as for digital sideband separation. Computes the LO Noise Rejection by 
# getting spectral data in a hot/cold test assuming an LO noise is present (it 
# can be injected with a noise source for example), and the model is calibrated.
# It then saves the results into a compress folder.

# imports
import os, corr, time, datetime, tarfile, shutil, json
import numpy as np
import matplotlib.pyplot as plt
import calandigital as cd
from dbm_load_constants import dbm_load_constants

# communication parameters
roach_ip        = '192.168.1.12'
boffile         = 'dss_2048ch_1520mhz.bof.gz'
noise_source_ip = '192.168.1.38'

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
lo_freq     = 9000 # MHz
acc_len     = 2**20
date_time   =  datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
datadir     = "dbm_lnr_noise " + date_time
pause_time  = 8.0 # should be > (1/bandwidth * FFT_size * acc_len * 2) in order 
                  # for the spectra to be fully computed after a tone change
load_consts = True
load_ideal  = False
caldir      = 'dbm_cal_noise 2020-02-28 19:57:09.tar.gz'

# derivative parameters
nchannels     = 2**bram_addr_width * len(bram_rf)
if_freqs      = np.linspace(0, bandwidth, nchannels, endpoint=False)
dBFS          = 6.02*adc_bits + 1.76 + 10*np.log10(nchannels)                

##########################
# Experiment Starts Here #
##########################
def main():
    global roach, rf_generator, fig, line3
    start_time = time.time()

    roach = cd.initialize_roach(roach_ip)
    noise_source = cd.Instrument(noise_source_ip)

    print("Setting up plotting and data saving elements...")
    fig, lines = create_figure()
    line3 = lines[6]
    make_data_directory()
    print("done")

    #####################
    # Start Measurement #
    #####################
    # loading calibration constants
    if load_consts:
        dbm_load_constants(roach, load_ideal, 1+0j, caldir)

    print("Setting accumulation register to " + str(acc_len) + "...")
    roach.write_int(acc_len_reg, acc_len)
    print("done")
    print("Reseting counter registers...")
    roach.write_int(cnt_rst_reg, 1)
    roach.write_int(cnt_rst_reg, 0)
    print("done")
    
    print("Turning noise source off...")
    noise_source.write('OUTPUT CH1,OFF')
    time.sleep(1)
    print("done")

    print("Getting lnr cold data...")
    rf_cold, lo_cold = get_lnrdata(lines[0], lines[2], lines[4])
    print("done")

    #raw_input("Change source to hot and press any key...")
    print("Turning noise source on...")
    noise_source.write('OUTPUT CH1,ON')
    time.sleep(1)
    print("done")

    print("Getting lnr hot data...")
    rf_hot, lo_hot = get_lnrdata(lines[1], lines[3], lines[5])
    print("done")

    print("Saving data...")
    np.savez(datadir+"/lnrdata", 
        rf_cold=rf_cold,lo_cold=lo_cold,
        rf_hot =rf_hot, lo_hot =lo_hot)
    print("done")

    print("Printing data...")
    print_data()
    print("done")

    print("Compressing data...")
    compress_data()
    print("done")

    print("Finished. Total time: " + str(int(time.time() - start_time)) + "[s]")
    print("Close plots to finish.")
    plt.show()

def create_figure():
    """
    Creates figure for plotting.
    """
    fig, [[ax0, ax1], [ax2, ax3]] = plt.subplots(2,2)
    fig.set_tight_layout(True)
    fig.show()
    fig.canvas.draw()

    # get line objects
    line0_cold, = ax0.plot([],[], label='cold')
    line0_hot,  = ax0.plot([],[], label='hot')
    line1_cold, = ax1.plot([],[], label='cold')
    line1_hot,  = ax1.plot([],[], label='hot')
    line2_cold, = ax2.plot([],[], label='cold')
    line2_hot,  = ax2.plot([],[], label='hot')
    line3,      = ax3.plot([],[])

    # set spectrometers axes
    ax0.set_xlim((0, bandwidth))     ; ax1.set_xlim((0, bandwidth))
    ax0.set_ylim((-80, 0))           ; ax1.set_ylim((-80, 0))
    ax0.grid()                       ; ax1.grid()
    ax0.set_xlabel('Frequency [MHz]'); ax1.set_xlabel('Frequency [MHz]')
    ax0.set_ylabel('Power [dBFS]')   ; ax1.set_ylabel('Power [dBFS]')
    ax0.set_title('RF spec')         ; ax1.set_title('LO spec')
    ax0.legend()                     ; ax1.legend()

    # Spec ratios axis
    ax2.set_xlim((0, bandwidth))     
    ax2.set_ylim((0, 80))            
    ax2.grid()                       
    ax2.set_xlabel('Frequency [MHz]')
    ax2.set_ylabel('Ratio [dB]') 
    ax2.set_title('Spec Ratios')         
    ax2.legend()

    # LNR axis
    ax3.set_xlim((0, bandwidth))     
    ax3.set_ylim((0, 80))            
    ax3.grid()                       
    ax3.set_xlabel('Frequency [MHz]')
    ax3.set_ylabel('LNR [dB]') 
    ax3.set_title('LNR')

    lines = [line0_cold, line0_hot, 
             line1_cold, line1_hot, 
             line2_cold, line2_hot, 
             line3]
    
    return fig, lines

def make_data_directory():
    """
    Make directory where to save all the lnr data.
    """
    os.mkdir(datadir)

    # make .json file with test info
    testinfo = {}
    testinfo["roach ip"]     = roach_ip
    testinfo["date time"]    = date_time
    testinfo["boffile"]      = boffile
    testinfo["bandwidth"]    = bandwidth
    testinfo["lo freq"]      = lo_freq
    testinfo["nchannels"]    = nchannels
    testinfo["acc len"]      = acc_len
    testinfo["load consts"]  = load_consts
    testinfo["load ideal"]   = load_ideal
    testinfo["caldir"]       = caldir

    with open(datadir + "/testinfo.json", "w") as f:
        json.dump(testinfo, f, indent=4, sort_keys=True)

def get_lnrdata(line0, line1, line2):
    """
    Get the lnr data assumimg a broadband noise signal is injected.
    The lnr data is the power of the input after applying the calibration
    constants (rf), and the negative of the constants (lo).    
    :param line0: line for first axis.
    :param line1: line for second axis.
    :param line1: line for third axis.
    :return: calibration data: a2, b2, and ab.
    """    
    # read data
    time.sleep(pause_time)
    rf = cd.read_interleave_data(roach, bram_rf,  bram_addr_width, 
                                 bram_word_width, pow_data_type)
    lo = cd.read_interleave_data(roach, bram_lo,  bram_addr_width, 
                                 bram_word_width, pow_data_type)


    # scale and dBFS data for plotting
    rf_plot = cd.scale_and_dBFS_specdata(rf, acc_len, dBFS)
    lo_plot = cd.scale_and_dBFS_specdata(lo, acc_len, dBFS)

    # compute lnr for plotting
    lnr_ratios = np.divide(lo, rf)

    # plot data
    line0.set_data(if_freqs, rf_plot)
    line1.set_data(if_freqs, lo_plot)
    line2.set_data(if_freqs, 10*np.log10(lnr_ratios))
    fig.canvas.draw()
    fig.canvas.flush_events()
        
    return rf, lo

def print_data():
    """
    Print the saved data to .pdf images for an easy check.
    """
    # get rf frequencies
    rf_freqs = lo_freq + if_freqs

    # get data
    lnrdata = np.load(datadir + "/lnrdata.npz")
    rf_cold = lnrdata['rf_cold']; rf_hot = lnrdata['rf_hot']
    lo_cold = lnrdata['lo_cold']; lo_hot = lnrdata['lo_hot']

    # compute LNR (using formula from Fujii, et al. 2017)
    lnr = (rf_hot - rf_cold) / (lo_hot - lo_cold) + 1

    # print LNR
    plt.figure()
    plt.plot(rf_freqs, 10*np.log10(lnr), 'b')
    plt.grid()                 
    plt.xlabel('Frequency [MHz]')
    plt.ylabel('LNR [dB]')     
    plt.savefig(datadir+'/lnr.pdf')
    plt.close()

    # set computed data into live plot
    line3.set_data(if_freqs, lnr)
    
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
