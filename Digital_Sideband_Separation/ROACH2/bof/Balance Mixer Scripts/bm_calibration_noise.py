# Script for noise calibration of digital balance mixer. It uses the same
# model as for digital sideband separation. Computes the magnitude ratio
# and phase difference of backend assuming a broadband noise signal is injected.
# It then saves the data into a compress folder, for later be used as 
# calibration constants with an lnr computation script.

# imports
import os, time, datetime, tarfile, shutil
import numpy as np
import matplotlib.pyplot as plt
import calandigital as cd

# communication parameters
roach_ip        = '192.168.1.10'
boffile         = 'dss_2048ch_1520mhz.bof.gz'

# model parameters
adc_bits           = 8
bandwidth          = 1080 # MHz
acc_len_reg        = 'cal_acc_len'
cnt_rst_reg        = 'cnt_rst'
bram_addr_width    = 8  # bits
bram_word_width    = 64 # bits
pow_data_type      = '>u8'
crosspow_data_type = '>i8'
bram_a2    = ['dout_a2_0', 'dout_a2_1', 'dout_a2_2', 'dout_a2_3', 
              'dout_a2_4', 'dout_a2_5', 'dout_a2_6', 'dout_a2_7']
babm_b2    = ['dout_b2_0', 'dout_b2_1', 'dout_b2_2', 'dout_b2_3', 
              'dout_b2_4', 'dout_b2_5', 'dout_b2_6', 'dout_b2_7']
bram_ab_re = ['dout_ab_re0', 'dout_ab_re1', 'dout_ab_re2', 'dout_ab_re3', 
              'dout_ab_re4', 'dout_ab_re5', 'dout_ab_re6', 'dout_ab_re7']
bram_ab_im = ['dout_ab_im0', 'dout_ab_im1', 'dout_ab_im2', 'dout_ab_im3', 
              'dout_ab_im4', 'dout_ab_im5', 'dout_ab_im6', 'dout_ab_im7']

# experiment parameters
lo_freq    = 8000 # MHz
acc_len    = 2**20
chnl_step  = 8
date_time  =  datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
datadir    = "bm_cal_noise " + date_time
pause_time = 8.0 # should be > (1/bandwidth * FFT_size * acc_len * 2) in order 
                 # for the spectra to be fully computed after a tone change

# derivative parameters
nchannels     = 2**bram_addr_width * len(bram_a2)
if_freqs      = np.linspace(0, bandwidth, nchannels, endpoint=False)
test_channels = range(1, nchannels, chnl_step)
if_test_freqs = if_freqs[test_channels]
dBFS          = 6.02*adc_bits + 1.76 + 10*np.log10(nchannels)

##########################
# Experiment Starts Here #
##########################
def main():
    global fig, line0, line1, line2, line3, roach, rf_generator
    start_time = time.time()

    roach = cd.initialize_roach(roach_ip)

    print("Setting up plotting and data saving elements...")
    fig, line0, line1, line2, line3 = create_figure()
    make_data_directory()
    print("done")

    #####################
    # Start Measurement #
    #####################
    print("Setting and resetting registers...")
    roach.write_int(acc_len_reg, acc_len)
    roach.write_int(cnt_rst_reg, 1)
    roach.write_int(cnt_rst_reg, 0)
    print("done")

    print("Getting calibration data...")
    a2, b2, ab = get_caldata()
    print("done")
        
    print("Turning off intruments...")
    rf_generator.write("outp off")
    print("done")

    print("Saving data...")
    np.savez(datadir+"/caldata", a2=a2, b2=b2, ab=ab)
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

    # set spectrometers axes
    ax0.set_xlim((0, bandwidth))     ; ax1.set_xlim((0, bandwidth))
    ax0.set_ylim((-80, 0))           ; ax1.set_ylim((-80, 0))
    ax0.grid()                       ; ax1.grid()
    ax0.set_xlabel('Frequency [MHz]'); ax1.set_xlabel('Frequency [MHz]')
    ax0.set_ylabel('Power [dBFS]')   ; ax1.set_ylabel('Power [dBFS]')
    ax0.set_title("ZDOK0 spec")      ; ax1.set_title("ZDOK1 spec")

    # set magnitude diference axis
    ax2.set_xlim((0, bandwidth))
    ax2.set_ylim((0, 2))     
    ax2.grid()                 
    ax2.set_xlabel('Frequency [MHz]')
    ax2.set_ylabel('Mag ratio [lineal]')     

    # set magnitude diference axis
    ax3.set_xlim((0, bandwidth))
    ax3.set_ylim((-180, 180))     
    ax3.grid()                 
    ax3.set_xlabel('Frequency [MHz]')
    ax3.set_ylabel('Angle diff [degrees]')

    # get line objects
    line0, = ax0.plot([],[])
    line1, = ax1.plot([],[])
    line2, = ax2.plot([],[])
    line3, = ax3.plot([],[])

    return fig, line0, line1, line2, line3

def make_data_directory():
    """
    Make directory where to save all the calibration data.
    """
    os.mkdir(datadir)

    # make .txt file with test info
    with open(datadir + "/testinfo.txt", "w") as f:
        f.write("roach ip:     " + roach_ip        + "\n")
        f.write("date time:    " + date_time       + "\n")
        f.write("boffile:      " + boffile         + "\n")
        f.write("bandwidth:    " + str(bandwidth)  + "\n")
        f.write("lo freq:      " + str(lo_freq)    + "\n")
        f.write("nchannels:    " + str(nchannels)  + "\n")
        f.write("acc len:      " + str(acc_len)    + "\n")
        f.write("chnl step:    " + str(chnl_step))

def get_caldata():
    """
    Get the calibration data assumimg a broadband noise signal is injected.
    The calibration data is the power of each input (a and b)
    and the cross-correlation of both inputs as a complex number (ab*).
    :return: calibration data: a2, b2, and ab.
    """
    # read data
    time.sleep(pause_time)
    a2    = read_interleave_data(roach, bram_a2,    bram_addr_width, 
                                 bram_word_width,   pow_data_type)
    b2    = read_interleave_data(roach, bram_b2,    bram_addr_width, 
                                 bram_word_width,   pow_data_type)
    ab_re = read_interleave_data(roach, bram_ab_re, bram_addr_width, 
                                 bram_word_width,   crosspow_data_type)
    ab_im = read_interleave_data(roach, bram_ab_im, bram_addr_width, 
                                 bram_word_width,   crosspow_data_type)

    # get crosspower as complex values
    ab = ab_re + 1j*ab_im

    # scale and dBFS data for plotting
    a2_plot = cd.scale_and_dBFS_specdata(a2, acc_len, dBFS)
    b2_plot = cd.scale_and_dBFS_specdata(b2, acc_len, dBFS)

    # compute input ratios for plotting
    ab_ratios = np.divide(ab, b2)
    
    # plot data
    line0.set_data(if_freqs, a2_plot)
    line1.set_data(if_freqs, b2_plot)
    line2.set_data(if_test_freqs[:i+1], np.abs(ab_ratios))
    line3.set_data(if_test_freqs[:i+1], np.angle(ab_ratios, deg=True))
    fig.canvas.draw()
    fig.canvas.flush_events()
    
    return a2, b2, ab

def print_data():
    """
    Print the saved data to .pdf images for an easy check.
    """
    # get rf frequencies
    rf_freqs = lo_freq + if_freqs

    # get data
    caldata = np.load(datadir + "/caldata.npz")
    a2_usb = caldata['a2']
    b2_usb = caldata['b2']
    ab_usb = caldata['ab']

    # compute ratios
    ab_ratios = ab / b2

    # print magnitude ratios
    plt.figure()
    plt.plot(rf_freqs, np.abs(ab_ratios), 'b')
    plt.grid()                 
    plt.xlabel('Frequency [MHz]')
    plt.ylabel('Mag ratio [lineal]')     
    plt.savefig(datadir+'/mag_ratios.pdf')
    
    # print angle difference
    plt.figure()
    plt.plot(rf_freqs, np.angle(ab_ratios, deg=True), 'b')
    plt.grid()                 
    plt.xlabel('Frequency [MHz]')
    plt.ylabel('Angle diff [degrees]')     
    plt.savefig(datadir+'/angle_diff.pdf')

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
