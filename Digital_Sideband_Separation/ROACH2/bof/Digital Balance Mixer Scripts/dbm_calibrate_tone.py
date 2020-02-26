# Script for tone calibration of digital balance mixer. It uses the same
# model as for digital sideband separation. Computes the magnitude ratio
# and phase difference of backend by sweeping a tone with a signal generator.
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
rf_generator_ip = '192.168.1.31'

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
bram_b2    = ['dout_b2_0', 'dout_b2_1', 'dout_b2_2', 'dout_b2_3', 
              'dout_b2_4', 'dout_b2_5', 'dout_b2_6', 'dout_b2_7']
bram_ab_re = ['dout_ab_re0', 'dout_ab_re1', 'dout_ab_re2', 'dout_ab_re3', 
              'dout_ab_re4', 'dout_ab_re5', 'dout_ab_re6', 'dout_ab_re7']
bram_ab_im = ['dout_ab_im0', 'dout_ab_im1', 'dout_ab_im2', 'dout_ab_im3', 
              'dout_ab_im4', 'dout_ab_im5', 'dout_ab_im6', 'dout_ab_im7']

# experiment parameters
lo_freq    = 8000 # MHz
acc_len    = 2**16
chnl_step  = 8
rf_power   = -10 #dBm
date_time  =  datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
datadir    = "dbm_cal_tone " + date_time
pause_time = 0.5 # should be > (1/bandwidth * FFT_size * acc_len * 2) in order 
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
    global roach, rf_generator, fig, line0, line1, line2, line3
    start_time = time.time()

    roach = cd.initialize_roach(roach_ip)
    rf_generator = cd.Instrument(rf_generator_ip)

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

    print("Setting instrumets power and outputs...")
    rf_generator.write("power " + str(rf_power))
    rf_generator.write("outp on")
    print("done")

    print("Starting tone sweep in upper sideband...")
    sweep_time = time.time()
    rf_freqs = lo_freq + if_freqs
    a2_usb, b2_usb, ab_usb = get_caldata(rf_freqs, "usb")
    print("done (" +str(int(time.time() - sweep_time)) + "[s])")
        
    print("Starting tone sweep in lower sideband...")
    sweep_time = time.time()
    rf_freqs = lo_freq - if_freqs
    a2_lsb, b2_lsb, ab_lsb = get_caldata(rf_freqs, "lsb")
    print("done (" +str(int(time.time() - sweep_time)) + "[s])")

    print("Turning off intruments...")
    rf_generator.write("outp off")
    print("done")

    print("Saving data...")
    np.savez(datadir+"/caldata", 
        a2_usb=a2_usb, b2_usb=b2_usb, ab_usb=ab_usb,
        a2_lsb=a2_lsb, b2_lsb=b2_lsb, ab_lsb=ab_lsb)
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
    fig, [[ax0, ax1], [ax2, ax3]] = plt.subplots(2,2)
    fig.set_tight_layout(True)
    fig.show()
    fig.canvas.draw()
    
    # get line objects
    line0, = ax0.plot([],[])
    line1, = ax1.plot([],[])
    line2, = ax2.plot([],[])
    line3, = ax3.plot([],[])
    
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
        f.write("chnl step:    " + str(chnl_step)  + "\n")
        f.write("rf generator: " + rf_generator_ip + "\n")
        f.write("rf power:     " + str(rf_power))

    # make rawdata folders
    os.mkdir(datadir + "/rawdata_usb")
    os.mkdir(datadir + "/rawdata_lsb")

def get_caldata(rf_freqs, sideband):
    """
    Sweep a tone through a sideband and get the calibration data.
    The calibration data is the power of each tone in both inputs (a and b)
    and the cross-correlation of both inputs as a complex number (ab*).
    The full sprecta measured for each tone is saved to data for debugging
    purposes.
    :param rf_freqs: frequencies of the tones to perform the sweep.
    :param sideband: sideband of the mesurement. Either USB or LSB
    :return: calibration data: a2, b2, and ab.
    """
    fig.canvas.set_window_title(sideband.upper() + " Sweep")

    a2_arr = []; b2_arr = []; ab_arr = []
    for i, chnl in enumerate(test_channels):
        # set test tone
        freq = rf_freqs[chnl]
        rf_generator.ask("freq " + str(freq*1e6) + ";*opc?") # freq must be in Hz
        time.sleep(pause_time)

        # read data
        a2    = read_interleave_data(roach, bram_a2,    bram_addr_width, 
                                     bram_word_width,   pow_data_type)
        b2    = read_interleave_data(roach, bram_b2,    bram_addr_width, 
                                     bram_word_width,   pow_data_type)
        ab_re = read_interleave_data(roach, bram_ab_re, bram_addr_width, 
                                     bram_word_width,   crosspow_data_type)
        ab_im = read_interleave_data(roach, bram_ab_im, bram_addr_width, 
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
        line0.set_data(if_freqs, a2_plot)
        line1.set_data(if_freqs, b2_plot)
        line2.set_data(if_test_freqs[:i+1], np.abs(ab_ratios))
        line3.set_data(if_test_freqs[:i+1], np.angle(ab_ratios, deg=True))
        fig.canvas.draw()
        fig.canvas.flush_events()
        
        # save data
        np.savez(datadir+"/rawdata_" + sideband + "/chnl_" + str(chnl), 
            a2=a2, b2=b2, ab_re=ab_re, ab_im=ab_im)

    # compute interpolations
    a2_arr = np.interp(if_freqs, if_test_freqs, a2_arr)
    b2_arr = np.interp(if_freqs, if_test_freqs, b2_arr)
    ab_arr = np.interp(if_freqs, if_test_freqs, ab_arr)

    return a2_arr, b2_arr, ab_arr

def print_data():
    """
    Print the saved data to .pdf images for an easy check.
    """
    # get rf frequencies
    rf_freqs_usb = lo_freq + if_freqs
    rf_freqs_lsb = lo_freq - if_freqs

    # get data
    caldata = np.load(datadir + "/caldata.npz")
    a2_usb = caldata['a2_usb']; a2_lsb = caldata['a2_lsb']
    b2_usb = caldata['b2_usb']; b2_lsb = caldata['b2_lsb']
    ab_usb = caldata['ab_usb']; ab_lsb = caldata['ab_lsb']

    # compute ratios
    ab_ratios_usb = ab_usb / b2_usb
    ab_ratios_lsb = ab_lsb / b2_lsb

    # print magnitude ratios
    plt.figure()
    plt.plot(rf_freqs_usb, np.abs(ab_ratios_usb), 'b')
    plt.plot(rf_freqs_lsb, np.abs(ab_ratios_lsb), 'b')
    plt.grid()                 
    plt.xlabel('Frequency [MHz]')
    plt.ylabel('Mag ratio [lineal]')     
    plt.savefig(datadir+'/mag_ratios.pdf')
    
    # print angle difference
    plt.figure()
    plt.plot(rf_freqs_usb, np.angle(ab_ratios_usb, deg=True), 'b')
    plt.plot(rf_freqs_lsb, np.angle(ab_ratios_lsb, deg=True), 'b')
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
