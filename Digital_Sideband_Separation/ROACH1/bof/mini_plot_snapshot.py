# Independent script for snapshot animated plotting in mini.
#
# Author: Franco Curotto. January 2020
# email: francocurotto@gmail.com

# imports
import corr, time
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# communication parameters
roach_ip = '192.168.1.11'
roach_port = 7147
boffile = 'corr2in_1024ch_500mhz.bof'
#boffile = 'dss_1024ch_500mhz.bof'
#boffile = 'snap2in.bof'
#boffile = 'spec2in_4096ch_500mhz.bof'
program_bof = True

# model parameters
snap_data_type = '>i1'
snapshots      = ['adcsnap0', 'adcsnap1']

# experiment parameters
nsamples = 256

##########################
# Experiment Starts Here #
##########################
def main():
    print("Setting up plotting and data saving elements...")
    fig, lines = create_figure(snapshots, nsamples, snap_data_type)
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
    def animate(_):
        # get snapshot data
        snapdata_list = read_snapshots(roach, snapshots, snap_data_type)
        for line, snapdata in zip(lines, snapdata_list):
            line.set_data(range(nsamples), snapdata[:nsamples])
        return lines

    ani = FuncAnimation(fig, animate, blit=True)
    plt.show()

def create_figure(snapnames, nsamples, dtype):
    """
    Create figure with the proper axes settings for plotting snaphots.
    """
    axmap = {1 : (1,1), 2 : (1,2), 4 : (2,2), 16 : (4,4)}
    nsnapshots = len(snapnames)

    fig, axes = plt.subplots(*axmap[nsnapshots], squeeze=False)
    fig.set_tight_layout(True)

    lines = []
    for snapname, ax in zip(snapnames, axes.flatten()):
        ax.set_xlim(0, nsamples)
        ax.set_ylim(np.iinfo(dtype).min-10, np.iinfo(dtype).max+10)
        ax.set_xlabel('Samples')
        ax.set_ylabel('Amplitude [a.u.]')
        ax.set_title(snapname)
        ax.grid()

        line, = ax.plot([], [], animated=True)
        lines.append(line)

    return fig, lines

def read_snapshots(roach, snapshots, dtype='>i1'):
    """
    Reads snapshot data from a list of snapshots names.
    :param roach: CalanFpga object to communicate with ROACH.
    :param snapshots: list of snapshot names to read.
    :param dtype: data type of data in snapshot. Must be Numpy compatible.
        My prefered format:
            (<, >):    little endian, big endian
            (i, u):    signed, unsigned
            (1,2,...): number of bytes
            e.g.: >i1: one byte, signed, big-endian
    :return: list of data arrays in the same order as the snapshot list. 
        Note: the data type is fixed to 8 bits as all of our ADC work at 
        that size. 
    """
    snapdata_list = []
    for snapshot in snapshots:
        rawdata  = roach.snapshot_get(snapshot, man_trig=True, man_valid=True)['data']
        snapdata = np.fromstring(rawdata, dtype=dtype)
        snapdata_list.append(snapdata)
    
    return snapdata_list

if __name__ == '__main__':
    main()
