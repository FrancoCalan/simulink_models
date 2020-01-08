# Independent script for digital sideband separation on mini telescope.
# This script computes the calibration constants for the DSS receiver
# and save them in a folder for later use with mini_compute_srr.py
#
# Author: Franco Curotto. December 2019
# email: francocurotto@gmail.com

# imports
import os, corr, time, datetime, vxi11, tarfile, shutil
import numpy as np
import matplotlib.pyplot as plt

# communication parameters
roach_ip = '192.168.1.10'
roach_port = 7147
boffile = 'corr2in_1024ch_500mhz.bof'
program_bof = True
rf_generator_ip = '192.168.1.31'
simulate_instruments = False

# model parameters
adc_bits = 8
adc_freq = 500 # MHz
acc_len_reg = 'acc_len'
cnt_rst_reg = 'cnt_rst'
bram_addr_width = 8  # bits
bram_word_width = 64 # bits
pow_data_type      = '>u8'
crosspow_data_type = '>i8'
bram_a2    = ['a2_0', 'a2_1', 'a2_2', 'a2_3']
bram_b2    = ['b2_0', 'b2_1', 'b2_2', 'b2_3']
bram_ab_re = ['ab_re0', 'ab_re1', 'ab_re2', 'ab_re3']
bram_ab_im = ['ab_im0', 'ab_im1', 'ab_im2', 'ab_im3']

# experiment parameters
#lo_freq = 3000 # MHz
lo_freq = 115271.2018 - 250 
acc_len = 2**16
chnl_step = 8
#rf_power = 19 # dBm
date_time =  datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
datadir = "mini_dss_test_cal " + date_time
pause_time = 0.6 # should be > (1/adc_freq * FFT_size * acc_len * 2) in order 
                 # for the spectra to be fully computed after a tone change

# derivative parameters
n_channels = 2**bram_addr_width * len(bram_a2)
if_freqs = np.linspace(0, adc_freq, n_channels, endpoint=False)
test_channels = range(1, n_channels, chnl_step)
if_test_freqs = if_freqs[test_channels]

##########################
# Experiment Starts Here #
##########################
def main():
    global fig, rf_generator, roach, line0, line1, line2, line3
    start_time = time.time()
    
    print("Setting up plotting and data saving elements...")
    fig, line0, line1, line2, line3 = create_figure()
    make_data_directory()
    print("done")

    print("Initializing ROACH communication...")
    roach = corr.katcp_wrapper.FpgaClient(roach_ip, roach_port)
    time.sleep(0.1)
    if not roach.is_connected():
        print("Unable to connect to ROACH :/")
        exit()
    print("done")
    
    if program_bof:
        print("Programming boffile " + boffile + " into ROACH...")
        roach.progdev(boffile)
    try:
        fpga_clock = roach.est_brd_clk()
    except RuntimeError:
        print("Unable to estimate FPGA clock :/.")
        print("1. Is the boffile programmed into the FPGA?")
        print("2. Is the boffile in the ROACH memory?")
        exit()
    print("done. Estimated FPGA clock: " + str(fpga_clock))
    
    print("Initializing other instruments communication...")
    if not simulate_instruments:
        rf_generator = vxi11.Instrument(rf_generator_ip)

        try:
            answer = rf_generator.ask("*IDN?")
        except:
            print("Unable to listen instrument " + str(rf_generator_ip) +
            ". It is not connected to the network?")
            exit()
    else:
        rf_generator = SimulatedInstrument(rf_generator_ip)
    print("done")
    
    #####################
    # Start measurement #
    #####################
    print("Setting accumulation register...")
    roach.write_int(acc_len_reg, acc_len)
    time.sleep(1)
    print("done")
    
    print("Reseting counters...")
    roach.write_int(cnt_rst_reg, 1)
    roach.write_int(cnt_rst_reg, 0)
    print("done")

    #print("Setting instrumets power and outputs...")
    #rf_generator.write("power " + str(rf_power))
    #rf_generator.write("outp on")
    #print("done")

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

    #print("Turning off intruments...")
    #rf_generator.write("outp off")
    #print("done")

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

    # set spectrometers axes
    ax0.set_xlim((0, adc_freq))      ; ax1.set_xlim((0, adc_freq))
    ax0.set_ylim((0, 80))            ; ax1.set_ylim((0, 80))
    ax0.grid()                       ; ax1.grid()
    ax0.set_xlabel('Frequency [MHz]'); ax1.set_xlabel('Frequency [MHz]')
    ax0.set_ylabel('Power [dB]')     ; ax1.set_ylabel('Power [dB]')
    ax0.set_title("In0 spec")        ; ax1.set_title("In1 spec")

    # set magnitude diference axis
    ax2.set_xlim((0, adc_freq))
    ax2.set_ylim((0, 2))     
    ax2.grid()                 
    ax2.set_xlabel('Frequency [MHz]')
    ax2.set_ylabel('Mag ratio [lineal]')     

    # set magnitude diference axis
    ax3.set_xlim((0, adc_freq))
    ax3.set_ylim((-180, 180))     
    ax3.grid()                 
    ax3.set_xlabel('Frequency [MHz]')
    ax3.set_ylabel('Angle diff [degrees]')

    # get line objects
    line0, = ax0.plot([],[])
    line1, = ax1.plot([],[])
    line2, = ax2.plot([],[])
    line3, = ax3.plot([],[])

    fig.set_tight_layout(True)
    plt.pause(0.001) # open plot window

    return fig, line0, line1, line2, line3

def make_data_directory():
    """
    Make directory where to save all the calibration data.
    """
    os.mkdir(datadir)

    # make .txt file with test info
    with open(datadir + "/testinfo.txt", "w") as f:
        f.write("date time:    " + date_time       + "\n")
        f.write("boffile:      " + boffile         + "\n")
        f.write("adc freq:     " + str(adc_freq)   + "\n")
        f.write("lo freq:      " + str(lo_freq)    + "\n")
        f.write("n channels:   " + str(n_channels) + "\n")
        f.write("acc len:      " + str(acc_len)    + "\n")
        f.write("chnl step:    " + str(chnl_step)  + "\n")
        f.write("rf generator: " + rf_generator_ip)

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
        rf_generator.write("freq " + str(1e6 * freq)) # freq must be in Hz
        time.sleep(pause_time)

        # read data
        a2    = read_bram_data(bram_a2,    pow_data_type)
        b2    = read_bram_data(bram_b2,    pow_data_type)
        ab_re = read_bram_data(bram_ab_re, crosspow_data_type)
        ab_im = read_bram_data(bram_ab_im, crosspow_data_type)

        # append data to arrays
        a2_arr.append(a2[chnl])
        b2_arr.append(b2[chnl])
        ab_arr.append(ab_re[chnl] + 1j*ab_im[chnl])

        # compute input ratios for plotting
        ab_ratios = np.divide(ab_arr, b2_arr)

        # plot data
        line0.set_data(if_freqs, 10*np.log10(a2 / float(acc_len)))
        line1.set_data(if_freqs, 10*np.log10(b2 / float(acc_len)))
        line2.set_data(if_test_freqs[:i+1], np.abs(ab_ratios))
        line3.set_data(if_test_freqs[:i+1], np.angle(ab_ratios, deg=True))
        plt.pause(0.001) # update plots

        # save data
        np.savez(datadir+"/rawdata_" + sideband + "/chnl_" + str(chnl), 
            a2=a2, b2=b2, ab_re=ab_re, ab_im=ab_im)

    # compute interpolations
    a2_arr = np.interp(if_freqs, if_test_freqs, a2_arr)
    b2_arr = np.interp(if_freqs, if_test_freqs, b2_arr)
    ab_arr = np.interp(if_freqs, if_test_freqs, ab_arr)

    return a2_arr, b2_arr, ab_arr

def read_bram_data(bram_list, data_type):
    """
    Read data from a list of brams and interleave the data in order to
    return in correctly ordered (as per typical spectrometer model).
    :param bram_list: list of bram list to read and interleave.
    :param data_type: data type of the read data.
    :return: array with the read data.
    """
    # get data
    depth = 2**bram_addr_width
    width = bram_word_width
    data_list = []
    for bram_name in bram_list:
        bram_data = roach.read(bram_name, depth*width/8, 0)   # raw byte data
        bram_data = np.frombuffer(bram_data, dtype=data_type) # integer data 
        data_list.append(bram_data)

    # interleave data list into a single array (this works, believe me)
    interleaved_data = np.vstack(data_list).reshape((-1,), order='F')

    return interleaved_data

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

class SimulatedInstrument():
    """
    Class used to simulate an SCPI instrument. Useful when you need to run the
    code but you don't want/can't connect to instruments.
    """
    def __init__(self, ip):
        print("Using simulated intrument for " + ip + ".")
    def write(self, command):
        pass

if __name__ == "__main__":
    main()
