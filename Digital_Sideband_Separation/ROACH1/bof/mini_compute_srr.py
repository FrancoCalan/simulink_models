# Independent script for digital sideband separation on mini telescope.
# This script computes load the calibration data from mini_get_calibration.py
# script and compute the sideband rejection ratio (SRR), for both ideal
# constants and calibrated constants.
# Author: Franco Curotto. December 2019
# email: francocurotto@gmail.com

# imports
import os, corr, time, datetime, vxi11, tarfile, shutil
import numpy as np
import matplotlib.pyplot as plt

# communication parameters
roach_ip = '192.168.1.11'
roach_port = 7147
boffile = 'dss_1024ch_500mhz.bof'
program_bof = True
rf_generator_ip = '192.168.1.34'
simulate_instruments = False

# model parameters
adc_bits = 8
adc_freq = 480 # MHz
acc_len_reg = 'acc_len'
cnt_rst_reg = 'cnt_rst'
bram_addr_width = 8  # bits
bram_word_width = 64 # bits
pow_data_type   = '>u8'
bram_a2         = ['a2_0', 'a2_1', 'a2_2', 'a2_3']
bram_b2         = ['b2_0', 'b2_1', 'b2_2', 'b2_3']
consts_nbits = 32
consts_binpt = 27
bram_consts_a_re = ['const_a0_bram_re', 'const_a1_bram_re',
                    'const_a2_bram_re', 'const_a3_bram_re']
bram_consts_a_im = ['const_a0_bram_im', 'const_a1_bram_im',
                    'const_a2_bram_im', 'const_a3_bram_im']
bram_consts_b_re = ['const_b0_bram_re', 'const_b1_bram_re',
                    'const_b2_bram_re', 'const_b3_bram_re']
bram_consts_b_im = ['const_b0_bram_im', 'const_b1_bram_im', 
                    'const_b2_bram_im', 'const_b3_bram_im']

# experiment parameters
lo_freq = 3000 # MHz
acc_len = 2**16
chnl_step = 8
rf_power = -10 # dBm
date_time =  datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
datadir = "mini_dss_test_srr " + date_time
caldir  = "mini_dss_test_cal 2019-12-12 11:03:02.tar.gz"
pause_time = 0.3 # should be > (1/adc_freq * FFT_size * acc_len * 2) in order 
                 # for the spectra to be fully computed after a tone change
do_ideal      = True
do_calibrated = True

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
        print("Programming boffile in ROACH...")
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

    print("Setting instrumets power and outputs...")
    rf_generator.write("power " + str(rf_power))
    rf_generator.write("outp on")
    print("done")

    if do_ideal:
        print("Computing SRR for ideal constants...")
        consts_a = -1j*np.ones(n_channels, dtype=np.complex64)
        consts_b = -1j*np.ones(n_channels, dtype=np.complex64)
        compute_srr(consts_a, consts_b, "ideal")
        print("done")
        
    if do_calibrated:
        print("Getting calibrated constants...")
        consts_a, consts_b = get_cal_constants()
        print("done")

        print("Computing SRR for calibrated constants...")
        compute_srr(consts_a, consts_b, "cal")
        print("done")
        
    print("Turning off intruments...")
    rf_generator.write("outp off")
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

    # SRR axes
    ax2.set_xlim((0, adc_freq))      ; ax3.set_xlim((0, adc_freq))
    ax2.set_ylim((0, 80))            ; ax3.set_ylim((0, 80))
    ax2.grid()                       ; ax3.grid()
    ax2.set_xlabel('Frequency [MHz]'); ax3.set_xlabel('Frequency [MHz]')
    ax2.set_ylabel('SRR [dB]')       ; ax3.set_ylabel('SRR [dB]')
    ax2.set_title("SRR USB")         ; ax3.set_title("SRR LSB")

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
        f.write("rf generator: " + rf_generator_ip + "\n")
        f.write("caldir:  "      + caldir)

    # make rawdata folders
    if do_ideal:
        os.mkdir(datadir + "/rawdata_ideal_usb")
        os.mkdir(datadir + "/rawdata_ideal_lsb")
    if do_calibrated:
        os.mkdir(datadir + "/rawdata_cal_usb")
        os.mkdir(datadir + "/rawdata_cal_lsb")

def get_cal_constants():
    """
    Retreive the calibration data from a .tar.gz file generated
    with the mini_get_calibration script, and compute the calibration
    constants.
    :return: complex calibration constants for input 0 (a) and input 1 (b).
    """
    # get data from .tar.gz and then remove file
    tar_file = tarfile.open(caldir)
    tar_file.extract('caldata.npz')
    caldata = np.load('caldata.npz')
    os.remove('caldata.npz')

    # compute the calibration constants from the calibration data
    # -1 * (ab*)* / aa* = -b/a = -LSB/USB 
    consts_a = -1 * np.conj(caldata['ab_usb']) / caldata['a2_usb']

    # -1 * ab* / bb* = -a/b = -USB/LSB
    consts_b = -1 * caldata['ab_lsb']  / caldata['b2_lsb'] 
    
    return consts_a, consts_b

def compute_srr(consts_a, consts_b, const_type):
    """
    Perform the computation of the SRR. The steps of the computation are:
    1. load constants
    2. sweep the tone and get the data (USB and LSB)
    3. save the data.
    :param consts_a: digital constants to load for input 0.
    :param consts_b: digital constants to load for input 1.
    :param const_type: label of the type of constant loaded (ideal or cal).
    """
    print("Loading constants...")
    load_comp_constants(consts_a, bram_consts_a_re, bram_consts_a_im)
    load_comp_constants(consts_b, bram_consts_b_re, bram_consts_b_im)
    print("done")

    print("Starting tone sweep in upper sideband...")
    sweep_time = time.time()
    rf_freqs = lo_freq + if_freqs
    a2_usb, b2_usb = get_srrdata(rf_freqs, const_type, "usb")
    print("done (" +str(int(time.time() - sweep_time)) + "[s])")
    
    print("Starting tone sweep in lower sideband...")
    sweep_time = time.time()
    rf_freqs = lo_freq - if_freqs
    a2_lsb, b2_lsb = get_srrdata(rf_freqs, const_type, "lsb")
    print("done (" +str(int(time.time() - sweep_time)) + "[s])")
    
    print("Saving data...")
    np.savez(datadir+"/srrdata_" + const_type, 
        a2_usb=a2_usb, b2_usb=b2_usb, a2_lsb=a2_lsb, b2_lsb=b2_lsb)
    print("done")

def load_comp_constants(consts, bram_re, bram_im):
    """
    Load complex constants into ROACH bram. Real and imaginary parts
    are loaded in separated bram blocks.
    :param consts: complex constants array.
    :param bram_re: bram block name for real part.
    :param bram_im: bram block name for imaginary part.
    """
    # separate real and imaginary
    consts_re = np.real(consts)
    consts_im = np.imag(consts)

    # convert data into fixed point representation
    consts_re_fixed = float2fixed(consts_re)
    consts_im_fixed = float2fixed(consts_im)

    # load data
    write_bram_data(bram_re, consts_re_fixed)
    write_bram_data(bram_im, consts_im_fixed)

def float2fixed(data):
    """
    Converts data from floating point to fixed point given by the model
    parameters for the calibration constants. No overflow checking is
    perfomed is done.
    """
    return (2**consts_binpt * data).astype('>i'+str(consts_nbits/8))

def write_bram_data(bram_list, data):
    """
    Write a data array into a list of brams. The data is deinterleaved 
    in order to determinate which elements go to which bram.
    :param bram_list: list of bram list to write.
    :param data: single dimension data array.
    """
    ndata  = len(data)
    nbrams = len(bram_list)

    # create a deinterleaved list form the array (this works, believe me)
    data_list = np.transpose(data.reshape(ndata/nbrams, nbrams))

    # write data into brams
    for bram, data_el in zip(bram_list, data_list):
        roach.write(bram, data_el.tobytes(), 0)

def get_srrdata(rf_freqs, const_type, sideband):
    """
    Sweep a tone through a sideband and get the sideband rejection data.
    The sideband rejection data is the power of each tone in both inputs
    (a and b) after they have passed through the calibrated constants 
    correction. The full sprecta measured for each tone is saved to data 
    for debugging purposes.
    :param rf_freqs: frequencies of the tones to perform the sweep.
    :param const_type: type of constants previously loaded (ideal, calibrated).
    :param sideband: sideband of the mesurement. Either USB or LSB.
    :return: srr data: a2, b2.
    """
    fig.canvas.set_window_title(const_type.upper() + " " + 
        sideband.upper() + " Sweep")

    # clear lines
    line3.set_data([],[])

    a2_arr = []; b2_arr = []
    for i, chnl in enumerate(test_channels):
        # set test tone
        freq = rf_freqs[chnl]
        rf_generator.write("freq " + str(1e6 * freq)) # freq must be in Hz
        time.sleep(pause_time)

        # read data
        a2 = read_bram_data(bram_a2, pow_data_type)
        b2 = read_bram_data(bram_b2, pow_data_type)

        # append data to arrays
        a2_arr.append(a2[chnl])
        b2_arr.append(b2[chnl])

        # plot data
        line0.set_data(if_freqs, 10*np.log10(a2 / float(acc_len)))
        line1.set_data(if_freqs, 10*np.log10(b2 / float(acc_len)))
        if sideband == 'usb':
            srr = np.divide(a2_arr, b2_arr, dtype=np.float)
            line2.set_data(if_test_freqs[:i+1], 10*np.log10(srr))
        elif sideband == 'lsb':
            srr = np.divide(b2_arr, a2_arr, dtype=np.float)
            line3.set_data(if_test_freqs[:i+1], 10*np.log10(srr))
        plt.pause(0.001) # update plots

        # save data
        np.savez(datadir+"/rawdata_" + const_type + "_" + sideband + 
        "/chnl_" + str(chnl), a2=a2, b2=b2)
    
    return a2_arr, b2_arr

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
    rf_freqs_usb = lo_freq + if_test_freqs
    rf_freqs_lsb = lo_freq - if_test_freqs

    # get data
    if do_ideal:
        srr_usb_ideal, srr_lsb_ideal = get_srr_from_data('ideal')
    if do_calibrated:
        srr_usb_cal, srr_lsb_cal = get_srr_from_data('cal')

    # plot srr
    plt.figure()
    if do_ideal:
        plt.plot(rf_freqs_usb, 10*np.log10(srr_usb_ideal), 'b', label='ideal')
        plt.plot(rf_freqs_lsb, 10*np.log10(srr_lsb_ideal), 'b')
    if do_calibrated:
        plt.plot(rf_freqs_usb, 10*np.log10(srr_usb_cal), 'g', label='cal')
        plt.plot(rf_freqs_lsb, 10*np.log10(srr_lsb_cal), 'g')
    plt.grid()                 
    plt.xlabel('Frequency [MHz]')
    plt.ylabel('SRR [dB]')     
    plt.legend()
    plt.savefig(datadir+'/srr.pdf')
    
def get_srr_from_data(const_type):
    """
    Compute srr from saved data.
    """
    # get data
    srrdata = np.load(datadir + "/srrdata_" + const_type + ".npz")
    a2_usb = srrdata['a2_usb']; a2_lsb = srrdata['a2_lsb']
    b2_usb = srrdata['b2_usb']; b2_lsb = srrdata['b2_lsb']

    # compute srr
    srr_usb = np.divide(a2_usb, b2_usb, dtype=np.float)
    srr_lsb = np.divide(b2_lsb, a2_lsb, dtype=np.float)

    return srr_usb, srr_lsb

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
