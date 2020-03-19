#!/usr/bin/python
# Script for SRR computation of digital sideband separating receiver with 
# multiple LO values and multiple LO stages.

# imports
import pyvisa, os, time, datetime, tarfile, shutil, json
import numpy as np
import matplotlib.pyplot as plt
import calandigital as cd
from dss_load_constants import dss_load_constants

# communication parameters
roach_ip           = '133.40.220.2'
#roach_ip           = None
boffile            = 'dss_2048ch_1520mhz.bof.gz'
lo1_generator_name = "GPIB0::20::INSTR"
lo2_generator_name = "GPIB0::5::INSTR"
rf_generator_name  = "GPIB0::11::INSTR"
rm = pyvisa.ResourceManager('@py')

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
# band 7 parameters
#lo1_freqs  = np.arange(275+20, 373, 16) # GHz
#lo1_freqs  = np.arange(275+20, 373, 100) # GHz
#lo1_mult   = 18
# band 8 parameters
#lo1_freqs  = np.arange(385+20, 500, 16) # GHz
lo1_freqs  = np.arange(400+20, 500, 100) # GHz
lo1_mult   = 18
#
#lo2_freqs   = np.arange(4, 20, 10) # GHz
lo2_freqs   = np.arange(4, 20, 20) # GHz
lo1_power   = 18 # dBm
lo2_power   = 16 # dBm
rf_mult     = 36
rf_power    = 7 # dBm
acc_len     = 2**16
chnl_step   = 16
date_time   =  datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
datadir     = "dss_srr " + date_time
pause_time  = 0.5 # should be > (1/bandwidth * FFT_size * acc_len * 2) in order 
                  # for the spectra to be fully computed after a tone change
load_consts = True
load_ideal  = False
caltar      = 'dss_cal 2020-03-19 18:13:07.tar.gz'

# derivative parameters
nchannels     = 2**bram_addr_width * len(bram_lsb)
if_freqs      = np.linspace(0, bandwidth, nchannels, endpoint=False) # MHz
test_channels = range(1, nchannels, chnl_step)
if_test_freqs = if_freqs[test_channels] # MHz
dBFS          = 6.02*adc_bits + 1.76 + 10*np.log10(nchannels)                

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
    roach.write_int(acc_len_reg, acc_len)
    print("done")
    print("Resseting counter registers...")
    roach.write_int(cnt_rst_reg, 1)
    roach.write_int(cnt_rst_reg, 0)
    print("done")

    print("Setting instruments power and outputs...")
    lo1_generator.write("power " + str(lo1_power))
    lo1_generator.write("freq mult " + str(lo1_mult))
    lo2_generator.write("power " + str(lo2_power))
    rf_generator.write("power " + str(rf_power))
    lo1_generator.write("outp on")
    lo2_generator.write("outp on")
    rf_generator.write("outp on")
    print("done")

def make_dss_multilo_measurements():
    """
    Makes the measurements for srr computation with multiple LOs.
    """
    for lo1_freq in lo1_freqs:
        # set lo1 frequency
        lo1_generator.ask("freq " + str(lo1_freq) + " ghz; *opc?")
        
        for lo2_freq in lo2_freqs:
            # set lo2 frequency
            lo2_generator.ask("freq " + str(lo2_freq) + " ghz; *opc?")

            # print setting
            print("Current LOs: LO1:" + str(lo1_freq) + "GHz," +
                              " LO2:" + str(lo2_freq) + "GHz")
            
            # make measurement subdirectory
            measname = "lo1_" + str(lo1_freq) + "ghz_lo2_" + \
                                str(lo2_freq) + "ghz"
            measdir = datadir + "/" + measname
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
    lo1_generator.write("outp off")
    lo2_generator.write("outp off")
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
    ax0.set_ylim((-85, 5))           ; ax1.set_ylim((-85, 5))
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
    testinfo["load consts"]        = load_consts
    testinfo["load ideal"]         = load_ideal
    testinfo["caltar"]             = caltar

    with open(datadir + "/testinfo.json", "w") as f:
        json.dump(testinfo, f, indent=4, sort_keys=True)

def make_dss_measurements(measdir, rf_freqs_usb, rf_freqs_lsb):
    """
    Makes the measurements for srr computation for a single set of LOs.
    :param measdir: directory where to save the data of this measurement
        (sub directory of main datadir).
    :param rf_freqs_usb: rf frequencies to measure in usb (GHz).
    :param rf_freqs_lsb: rf frequencies to measure in lsb (GHz).
    """
    # loading calibration constants
    if load_consts:
        caldir = os.path.basename(measdir)
        dss_load_constants(roach, load_ideal, 0-1j, caltar, caldir+"/")

    print("Starting tone sweep in upper sideband...")
    sweep_time = time.time()
    usb_toneusb, lsb_toneusb = get_srrdata(measdir, rf_freqs_usb, "usb")
    print("done (" +str(int(time.time() - sweep_time)) + "[s])")
        
    print("Starting tone sweep in lower sideband...")
    sweep_time = time.time()
    usb_tonelsb, lsb_tonelsb = get_srrdata(measdir, rf_freqs_lsb, "lsb")
    print("done (" +str(int(time.time() - sweep_time)) + "[s])")

    print("Saving data...")
    np.savez(measdir+"/srrdata",
        usb_toneusb=usb_toneusb, lsb_toneusb=lsb_toneusb,
        usb_tonelsb=usb_tonelsb, lsb_tonelsb=lsb_tonelsb)
    print("done")

    print("Printing data...")
    print_data(measdir)
    print("done")

def get_srrdata(measdir, rf_freqs, tone_sideband):
    """
    Sweep a tone through a sideband and get the srr data.
    The srr data is the power of each tone after applying the calibration
    constants for each sideband (usb and lsb).
    The full sprecta measured for each tone is saved to data for debugging
    purposes.
    :param measdir: directory where to save the raw data.
    :param rf_freqs: frequencies of the tones to perform the sweep.
    :param tone_sideband: sideband of the injected test tone. Either USB or LSB
    :return: srr data: usb and lsb.
    """
    fig.canvas.set_window_title(tone_sideband.upper() + " Tone Sweep")

    usb_arr = []; lsb_arr = []
    for i, chnl in enumerate(test_channels):
        # set test tone
        freq = rf_freqs[chnl]
        rf_generator.ask("freq " + str(freq) + " ghz; *opc?") 
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
        np.savez(measdir+"/rawdata_tone_" + tone_sideband + "/chnl_" + str(chnl), 
            usb=usb, lsb=lsb)

    # compute interpolations
    usb_arr = np.interp(if_freqs, if_test_freqs, usb_arr)
    lsb_arr = np.interp(if_freqs, if_test_freqs, lsb_arr)

    return usb_arr, lsb_arr

def print_data(measdir):
    """
    Print the saved data to .pdf images for an easy check.
    :param datadir: directory where to read the data of single measurement
    and save the image (sub directory of main datadir).
    """
    # get data
    srrdata = np.load(measdir + "/srrdata.npz")
    usb_toneusb = srrdata['usb_toneusb']; lsb_toneusb = srrdata['lsb_toneusb']
    usb_tonelsb = srrdata['usb_tonelsb']; lsb_tonelsb = srrdata['lsb_tonelsb']

    # compute ratios
    srr_usb = usb_toneusb / lsb_toneusb
    srr_lsb = lsb_tonelsb / usb_tonelsb

    # print SRR
    plt.figure()
    plt.plot(if_freqs, 10*np.log10(srr_usb), 'b', label="USB")
    plt.plot(if_freqs, 10*np.log10(srr_lsb), 'r', label="LSB")
    plt.grid()                 
    plt.xlabel('Frequency [MHz]')
    plt.ylabel('SRR [dB]')     
    plt.legend()
    plt.savefig(measdir+'/srr.pdf')
    plt.close()
    
def print_multilo_data():
    """
    Print the saved data from all LO settings to .pdf image.
    """
    # create SRR figure
    fig1, ax1 = plt.subplots(1,1)
    ax1.grid()                 
    ax1.set_xlabel('Frequency [MHz]')
    ax1.set_ylabel('SRR [dB]')
    
    for lo1_freq in lo1_freqs:
        for lo2_freq in lo2_freqs:
            # get measurement subdirectory
            measname = "lo1_" + str(lo1_freq) + "ghz_lo2_" + \
                                str(lo2_freq) + "ghz"
            measdir = datadir + "/" + measname
            
            # compute rf frequencies
            rf_freqs_usb = lo1_freq + lo2_freq + (if_freqs/1e3) # GHz
            rf_freqs_lsb = lo1_freq - lo2_freq - (if_freqs/1e3) # GHz

            # get data
            srrdata = np.load(measdir + "/srrdata.npz")
            usb_toneusb = srrdata['usb_toneusb']
            lsb_toneusb = srrdata['lsb_toneusb']
            usb_tonelsb = srrdata['usb_tonelsb']
            lsb_tonelsb = srrdata['lsb_tonelsb']
        
            # compute SRR
            srr_usb = usb_toneusb / lsb_toneusb
            srr_lsb = lsb_tonelsb / usb_tonelsb

            # plot SRR
            ax1.plot(rf_freqs_usb, 10*np.log10(srr_usb), 'b')
            ax1.plot(rf_freqs_lsb, 10*np.log10(srr_lsb), 'r')
            
    # print figures
    fig1.savefig(datadir+'/srr.pdf')

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
