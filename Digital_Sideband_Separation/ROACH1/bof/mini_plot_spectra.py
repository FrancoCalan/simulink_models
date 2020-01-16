# Independent script for spectra animated plotting in mini.
#
# Author: Franco Curotto. January 2020
# email: francocurotto@gmail.com

# imports
import corr, time
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# communication parameters
roach_ip = '192.168.1.10'
roach_port = 7147
boffile = 'corr2in_1024ch_500mhz.bof'
#boffile = 'dss_1024ch_500mhz.bof'
program_bof = True

# model parameters
adc_bits = 8
bandwidth = 480 # MHz
acc_len_reg = 'acc_len'
cnt_rst_reg = 'cnt_rst'
bram_addr_width = 8  # bits
bram_word_width = 64 # bits
pow_data_type   = '>u8'
bram_a2    = ['a2_0', 'a2_1', 'a2_2', 'a2_3']
bram_b2    = ['b2_0', 'b2_1', 'b2_2', 'b2_3']

# experiment parameters
acc_len = 2**16

# derivative parameters
nbrams    = len(bram_a2)
nchannels = 2**bram_addr_width * nbrams
freqs     = np.linspace(0, bandwidth, nchannels, endpoint=False)
dBFS      = 6.02*adc_bits + 1.76 + 10*np.log10(nchannels)
specbrams_list = [bram_a2, bram_b2]

##########################
# Experiment Starts Here #
##########################
def main():
    print("Setting up plotting and data saving elements...")
    fig, lines = create_figure(2, bandwidth, dBFS)
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

    def animate(_):
        for line, specbrams in zip(lines, specbrams_list):
            # get spectral data
            specdata = read_interleave_data(roach, specbrams, 
                bram_addr_width, bram_word_width, pow_data_type)
            specdata = scale_and_dBFS_specdata(specdata, acc_len, 
                adc_bits, nchannels)
            line.set_data(freqs, specdata)
        return lines

    ani = FuncAnimation(fig, animate, blit=True)
    plt.show()

def create_figure(nspecs, bandwidth, dBFS):
    """
    Create figure with the proper axes settings for plotting spectra.
    """
    axmap = {1 : (1,1), 2 : (1,2), 4 : (2,2), 16 : (4,4)}

    fig, axes = plt.subplots(*axmap[nspecs], squeeze=False)
    fig.set_tight_layout(True)

    lines = []
    for i, ax in enumerate(axes.flatten()):
        ax.set_xlim(0, bandwidth)
        ax.set_ylim(-dBFS-2, 0)
        ax.set_xlabel('Frequency [MHz]')
        ax.set_ylabel('Power [dBFS]')
        ax.set_title('In ' + str(i))
        ax.grid()

        line, = ax.plot([], [], animated=True)
        lines.append(line)

    return fig, lines

def read_interleave_data(roach, brams, awidth, dwidth, dtype):
    """
    Reads data from a list of brams and interleave the data in order to return 
    in correctly ordered (as per typical spectrometer models in ROACH).
    :param brams: list of bram list to read and interleave.
    :param awidth: width of bram address in bits.
    :param dwidth: width of bram data in bits.
    :param data_type: data type of data in brams. See read_snapshots().
    :return: array with the read data.
    """
    depth = 2**awidth
    bramdata_list = []

    # get data
    for bram in brams:
        rawdata  = roach.read(bram, depth*dwidth/8, 0)
        bramdata = np.frombuffer(rawdata, dtype=dtype)
        bramdata = bramdata.astype(np.float)
        bramdata_list.append(bramdata)

    # interleave data list into a single array (this works, believe me)
    interleaved_data = np.vstack(bramdata_list).reshape((-1,), order='F')

    return interleaved_data

def scale_and_dBFS_specdata(data, acclen, nbits, nchannels):
    """
    Scales spectral data by an accumulation length, and converts
    the data to dBFS. Used for plotting spectra.
    :param data: spectral data to convert. Must be Numpy array.
    :param acclen: accumulation length of spectrometer. 
        Used to scale the data.
    :param nbits: number of bits used to sample the data (ADC bits).
    :param nchannels: number of channels of the spectrometer.
    :return: scaled data in dBFS.
    """
    # scale data 
    data = data / acclen

    # convert data to dBFS
    dBFS = 6.02*nbits + 1.76 + 10*np.log10(nchannels)
    data = 10*np.log10(data+1) - dBFS

    return data

if __name__ == "__main__":
    main()
