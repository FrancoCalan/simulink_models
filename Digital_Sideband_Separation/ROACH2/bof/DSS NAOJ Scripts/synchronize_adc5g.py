#!/usr/bin/python
# Script to synchronize the 2 ADC5G of ROACH2 for the specific
# NAOJ experiment setup.
import time
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats
import calandigital as cd
from dss_multilo_parameters import *

def main():
    start_time = time.time()

    make_pre_measurements_actions()
    synchronize_adc5g()
    make_post_measurements_actions()

    print("Finished. Total time: " + str(int(time.time() - start_time)) + "[s]")

def make_pre_measurements_actions():
    """
    Makes all the actions in preparation for the measurements:
    - initizalize ROACH and generator communications.
    - creating plotting and data
    - setting initial registers in FPGA
    - turning on generator power
    """
    global roach, rf_generator, lo1_generator, lo2_generator, fig, lines

    roach = cd.initialize_roach(roach_ip)
    lo1_generator = rm.open_resource(lo1_generator_name)
    lo2_generator = rm.open_resource(lo2_generator_name)
    rf_generator  = rm.open_resource(rf_generator_name)

    print("Setting up plotting elements...")
    fig, lines = create_figure()
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

def synchronize_adc5g():
    """
    Iteratively measure the angle difference vs frequency and compute the 
    necessary delay to synchronize adcs.
    """
    # set the LO frequiencies. Use the first LO combination
    lo1_freq = lo1_freqs[0]; lo2_freq = lo2_freqs[0]
    lo1_generator.ask("freq " + str(lo1_freq) + " ghz; *opc?")
    lo2_generator.ask("freq " + str(lo2_freq) + " ghz; *opc?")

    # print setting
    print("LO combination used: LO1:" + str(lo1_freq) + "GHz," +
                              " LO2:" + str(lo2_freq) + "GHz")

    # compute the rf frequencies where to sweep the tone. Use USB
    rf_freqs = lo1_freq + lo2_freq + (if_freqs/1e3) # GHz

    # Main synchronization loop
    print("Synchronizing ADCs...")
    while True:
        print("Starting tone sweep...")
        sweep_time = time.time()
        ab_ratios = get_caldata(rf_freqs)
        print("done (" +str(int(time.time() - sweep_time)) + "[s])")

        # get delays between adcs
        delay = compute_adc_delay(if_sync_freqs, ab_ratios, bandwidth)

        # check adcs sync status, apply delay if necesary
        if delay == 0:
            print("ADCs successfully synchronized!")
            break
        elif delay > 0: # if delay is positive adc1 is ahead, hence delay adc1
            current_delay = roach.read_int(delay_regs[1])
            roach.write_int(delay_regs[1], current_delay + delay)
        else: # (delay < 0) if delay is negative adc0 is ahead, hence delay adc0
            current_delay = roach.read_int(delay_regs[0])
            roach.write_int(delay_regs[0], current_delay + -1*delay)

def make_post_measurements_actions():
    """
    Makes all the actions required after measurements:
    - turn off sources
    """
    print("Turning off instruments...")
    lo1_generator.write("freq:mult 1")
    rf_generator.write("freq:mult 1")
    lo1_generator.write("outp off")
    lo2_generator.write("outp off")
    rf_generator.write("outp off")
    rm.close()
    print("done")

def create_figure():
    """
    Create figure with the proper axes for the synchronization procedure.
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

def get_caldata(rf_freqs):
    """
    Sweep a tone through a sideband and get the complex ratio of first (a) and
    second (b) input. It is later used to compute the adc delay using the angle
    difference information.
    :param rf_freqs: frequencies of the tones to perform the sweep (GHz).
    :return ab_ratios: complex ratios between a and b.
    """
    a2_arr = []; b2_arr = []; ab_arr = []
    for i, chnl in enumerate(sync_channels):
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
        ab_ratios = np.divide(np.conj(ab_arr), a2_arr) # (ab*)* /aa* = a*b / aa* = b/a

        # plot data
        lines[0].set_data(if_freqs, a2_plot)
        lines[1].set_data(if_freqs, b2_plot)
        lines[2].set_data(if_sync_freqs[:i+1], np.abs(ab_ratios))
        lines[3].set_data(if_sync_freqs[:i+1], np.angle(ab_ratios, deg=True))
        fig.canvas.draw()
        fig.canvas.flush_events()
        
    return ab_ratios

def compute_adc_delay(freqs, ratios, bandwidth):
    """
    Compute the adc delay between two unsynchronized adcs. It is done by 
    computing the slope of the phase difference with respect the frequency, 
    and then it translates this value into an integer delay in number of 
    samples.
    :param freqs: frequency array in which the sideband ratios where computed.
    :param ratios: complex ratios array of the adcs. The complex ratios is the 
        complex division of an spectral channel from adc0 with adc1.
    :param bandwidth: spectrometer bandwidth.
    :return: adc delay in number of samples.
    """
    phase_diffs = np.unwrap(np.angle(ratios))
    linregress_results = scipy.stats.linregress(freqs, phase_diffs)
    angle_slope = linregress_results.slope
    delay = int(round(angle_slope * 2*bandwidth / (2*np.pi))) # delay = dphi/df * Fs / 2pi
    print "Computed delay: " + str(delay)
    return delay
   
if __name__ == '__main__':
    main()
