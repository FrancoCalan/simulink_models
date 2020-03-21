#!/usr/bin/python
# Script for making a hotcold measurement of sideband separating receiver.
# Used to make Kerr correction in the computation of sideband rejection 
# ratio (SRR). See ALMA memo 357:
# http://legacy.nrao.edu/alma/memos/html-memos/alma357/memo357.pdf

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
    global roach, lo1_generator, lo2_generator, fig, lines

    roach = cd.initialize_roach(roach_ip)
    lo1_generator = rm.open_resource(lo1_generator_name)
    lo2_generator = rm.open_resource(lo2_generator_name)
    chopper       = rm.open_resource(chopper_name)

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
    lo1_generator.write("freq mult " + str(lo1_mult))
    lo2_generator.write("power " + str(lo2_power))
    lo1_generator.write("outp on")
    lo2_generator.write("outp on")
    print("done")

def make_dss_multilo_measurements():
    """
    Makes the hot cold measurements for dss with multiple LOs.
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
            measdir = hotcold_datadir + "/" + measname
            os.mkdir(measdir)
            
            # make measurement
            make_dss_measurements(measdir)

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
    print("done")

    print("Compressing data...")
    compress_data(hotcold_datadir)
    print("done")

def create_figure():
    """
    Creates figure for plotting.
    """
    fig, [ax0, ax1] = plt.subplots(1,2)
    fig.set_tight_layout(True)
    fig.show()
    fig.canvas.draw()
    
    # get line objects
    line0, = ax0.plot([],[], 'b', label='cold') # in0 cold
    line1, = ax1.plot([],[], 'b', label='cold') # in1 cold
    line2, = ax0.plot([],[], 'r', label='hot')  # in0 hot
    line3, = ax1.plot([],[], 'r', label='hot')  # in1 hot
    lines  = [line0, line1, line2, line3] 
    
    # set spectrometers axes
    ax0.set_xlim((0, bandwidth))     ; ax1.set_xlim((0, bandwidth))
    ax0.set_ylim((-85, 5))           ; ax1.set_ylim((-85, 5))
    ax0.grid()                       ; ax1.grid()
    ax0.set_xlabel('Frequency [MHz]'); ax1.set_xlabel('Frequency [MHz]')
    ax0.set_ylabel('Power [dBFS]')   ; ax1.set_ylabel('Power [dBFS]')
    ax0.set_title('ZDOK0 spec')      ; ax1.set_title('ZDOK1 spec')
    ax0.legend()                     ; ax1.legend()

    return fig, lines

def make_data_directory():
    """
    Make directory where to save all the hot cold data.
    """
    os.mkdir(hotcold_datadir)

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
    testinfo["chopper name"]       = chopper_name

    with open(hotcold_datadir + "/testinfo.json", "w") as f:
        json.dump(testinfo, f, indent=4, sort_keys=True)

def make_dss_measurements(measdir):
    """
    Makes the hot cold measurements for dss for a single set of LOs.
    :param measdir: directory where to save the data of this measurement
        (sub directory of main hotcold_datadir).
    """
    print("Setting setting chopper to cold...")
    # TODO: set chopper to cold
    print("done")

    print("Getting spectral data cold...")
    a2_cold = cd.read_interleave_data(roach, bram_a2,    bram_addr_width, 
                                      bram_word_width,   pow_data_type)
    b2_cold = cd.read_interleave_data(roach, bram_b2,    bram_addr_width, 
                                      bram_word_width,   pow_data_type)
    print("done")
        
    print("Setting setting chopper to cold...")
    # TODO: set chopper to cold
    print("done")

    print("Getting spectral data hot...")
    a2_hot = cd.read_interleave_data(roach, bram_a2,    bram_addr_width, 
                                     bram_word_width,   pow_data_type)
    b2_hot = cd.read_interleave_data(roach, bram_b2,    bram_addr_width, 
                                     bram_word_width,   pow_data_type)
    print("done")

    # scale and dBFS data for plotting
    a2_cold_plot = cd.scale_and_dBFS_specdata(a2_cold, acc_len, dBFS)
    b2_cold_plot = cd.scale_and_dBFS_specdata(b2_cold, acc_len, dBFS)
    a2_hot_plot  = cd.scale_and_dBFS_specdata(a2_hot,  acc_len, dBFS)
    b2_hot_plot  = cd.scale_and_dBFS_specdata(b2_hot,  acc_len, dBFS)

    # plot data
    lines[0].set_data(if_freqs, a2_cold_plot)
    lines[1].set_data(if_freqs, b2_cold_plot)
    lines[2].set_data(if_freqs, a2_hot_plot)
    lines[3].set_data(if_freqs, b2_hot_plot)
    fig.canvas.draw()
    fig.canvas.flush_events()
    
    print("Saving data...")
    np.savez(measdir+"/hotcold_data", 
        a2_cold=a2_cold, b2_cold=b2_cold, a2_hot=a2_hot, b2_hot=b2_hot)
    print("done")

    print("Printing data...")
    print_data(measdir)
    print("done")

def print_data(measdir):
    """
    Print the saved data to .pdf images for an easy check.
    :param measdir: directory where to read the data of single measurement
    and save the image (sub directory of main hotcold_datadir).
    """
    # get data
    hotcold_data = np.load(measdir + "/hotcold_data.npz")
    a2_cold = hotcold_data['a2_cold']; b2_cold = hotcold_data['b2_cold']
    a2_hot  = hotcold_data['a2_hot'];  b2_hot =  hotcold_data['b2_hot']
    
    # compute power levels
    pow_a2_cold = cd.scale_and_dBFS_specdata(a2_cold, acc_len, dBFS)
    pow_b2_cold = cd.scale_and_dBFS_specdata(b2_cold, acc_len, dBFS)
    pow_a2_hot  = cd.scale_and_dBFS_specdata(a2_hot,  acc_len, dBFS)
    pow_b2_hot  = cd.scale_and_dBFS_specdata(b2_hot,  acc_len, dBFS)

    # print power level
    plt.figure()
    plt.plot(if_freqs, pow_a2_cold, 'blue',     label="USB cold")
    plt.plot(if_freqs, pow_b2_cold, 'darkblue', label="LSB cold")
    plt.plot(if_freqs, pow_a2_hot,  'red',      label="USB hot")
    plt.plot(if_freqs, pow_b2_hot,  'darkred',  label="LSB hot")
    plt.grid()                 
    plt.xlabel('Frequency [MHz]')
    plt.ylabel('Power [dBFS]')
    plt.legend()
    plt.savefig(measdir+'/power_lev.pdf')
    plt.close()

def print_multilo_data():
    """
    Print the saved data from all LO settings to .pdf image.
    """
    # create power level figure
    fig1, ax1 = plt.subplots(1,1)
    ax1.grid()                 
    ax1.set_xlabel('Frequency [MHz]')
    ax1.set_ylabel('Power [dBFS]')
    ax1.plot([], [], 'blue',     label="USB cold")
    ax1.plot([], [], 'darkblue', label="LSB cold")
    ax1.plot([], [], 'red',      label="USB hot")
    ax1.plot([], [], 'darkred',  label="LSB hot")
    ax1.legend()
    
    for lo1_freq in lo1_freqs:
        for lo2_freq in lo2_freqs:
            # get measurement subdirectory
            measname = "lo1_" + str(lo1_freq) + "ghz_lo2_" + \
                                str(lo2_freq) + "ghz"
            measdir = hotcold_datadir + "/" + measname
            
            # compute rf frequencies
            rf_freqs_usb = lo1_freq + lo2_freq + (if_freqs/1e3) # GHz
            rf_freqs_lsb = lo1_freq - lo2_freq - (if_freqs/1e3) # GHz

            # get data
            hotcold_data = np.load(measdir + "/hotcold_data.npz")
            a2_cold = hotcold_data['a2_cold']
            b2_cold = hotcold_data['b2_cold']
            a2_hot  = hotcold_data['a2_hot']
            b2_hot  = hotcold_data['b2_hot']
        
            # compute power levels
            pow_a2_cold = cd.scale_and_dBFS_specdata(a2_cold, acc_len, dBFS)
            pow_b2_cold = cd.scale_and_dBFS_specdata(b2_cold, acc_len, dBFS)
            pow_a2_hot  = cd.scale_and_dBFS_specdata(a2_hot,  acc_len, dBFS)
            pow_b2_hot  = cd.scale_and_dBFS_specdata(b2_hot,  acc_len, dBFS)

            # plot power levels
            plt.plot(rf_freqs_usb, pow_a2_cold, 'blue',     label="USB cold")
            plt.plot(rf_freqs_lsb, pow_b2_cold, 'darkblue', label="LSB cold")
            plt.plot(rf_freqs_usb, pow_a2_hot,  'red',      label="USB hot")
            plt.plot(rf_freqs_lsb, pow_b2_hot,  'darkred',  label="LSB hot")
            
    # print figures
    fig1.savefig(hotcold_datadir+'/power_lev.pdf')

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
