import calandigital as cd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


# communication parameters
roach_ip = None
boffile  = 'dss_2048ch_1520mhz.bof.gz'

# model parameters
adc_bits  = 8
bandwidth = 600.0 # MHz
fcenter   = 1500 # MHz
nchnls    = 64
count_reg = "cnt_rst"
acc_regs = ["acc_len0", "acc_len1", "acc_len2", "acc_len3", 
    "acc_len4", "acc_len5", "acc_len6", "acc_len7", 
    "acc_len8", "acc_len9", "acc_len10"]
det_regs = ["frb_detect0", "frb_detect1", "frb_detect2", 
    "frb_detect3", "frb_detect4", "frb_detect5", "frb_detect6",
    "frb_detect7", "frb_detect8", "frb_detect9", 
    "frb_detect10"]
bram_list = ["ACC0", "ACC1", "ACC2", "ACC3", "ACC4", "ACC5", 
    "ACC6", "ACC7", "ACC9", "ACC9", "ACC10"]
bram_addr_width = 10 # bits
bram_word_width = 32 # bits
bram_data_type  = '>u4'

# experiment parameters
k     = 4.16e6 # formula constant [MHz^2*pc^-1*cm^3*ms]
DMs   = range(0, 550, 50)
ylim  = (-10,100)
theta = 60

# derivative parameters
flow    = fcenter - bandwidth/2 # MHz
fhigh   = fcenter + bandwidth/2 # MHz
iffreqs = np.linspace(0, bandwidth, nchnls, endpoint=False)
rffreqs = iffreqs + flow
Ts      = 1/(2*bandwidth) # us
tspec   = Ts*nchnls # us

def main():
    # initialize roach
    roach = cd.initialize_roach(roach_ip, boffile=boffile)

    # create figures
    fig, lines = create_figure()
    
    # initial setting of registers
    print("Setting accumulation registers.")
    accs = compute_accs()
    for acc, acc_reg in zip(accs, acc_regs):
        roach.write_int(acc_reg, acc)
    print("Resseting counter registers.")
    roach.write_int(count_reg, 1)
    roach.write_int(count_reg, 0)
    print("done.")

    # animation definition
    def animate(_):
        for line, bram in zip(lines, bram_list):
            # get spectral data
            frbdata = cd.read_data(roach, bram, 
                bram_addr_width, bram_word_width,   
                bram_data_type)
            frbdata = 10*np.log10(frbdata+1)
            line.set_data(range(len(frbdata)),frbdata)
        return lines

    ani = FuncAnimation(fig, animate, blit=True)
    plt.show()

def create_figure():
    # create figure and axes
    #fig, axes = plt.subplots(4, 3, sharey=True, sharex=True)
    fig = plt.figure()
    axes = []
    for i in range(len(DMs)):
        axes.append(fig.add_subplot(4,3,i+1))
    fig.set_tight_layout(True)

    # set axes parameters
    lines = []
    for i,ax,dm in zip(range(len(DMs)),axes,DMs):
        ax.set_xlim(0, 2**bram_addr_width)
        if i in [0,3,6,9]:
            ax.set_ylabel('Power [dB]')
        ax.set_title("DM: " + str(dm))
        ax.set_ylim(ylim)
        ax.grid()
        line, = ax.plot([], [], animated=True)
        ax.plot([0,2**bram_addr_width], [theta, theta])
        lines.append(line)

    return fig, lines

def compute_accs():
    """
    Compute the necessary accumulation for each DM for
    proper dedispersion.
    """
    # use higher frequency because it requires the lowest
    # accumulation
    binsize = iffreqs[1]
    fbin_low  = rffreqs[-2] + binsize/2
    fbin_high = rffreqs[-1] + binsize/2
    accs = []
    for dm in DMs:
        disptime = disp_time(dm, fbin_low, fbin_high)
        acc = disptime*1e6 / tspec
        accs.append(int(round(acc)))
    
    # adjust DM 0 to the next acc
    accs[0] = accs[1]
    print("Computed accumulations: " + str(accs))
    return accs
        
def disp_time(dm, flow, fhigh):
    """
    Compute dispersed FRB duration.
    :param dm: Dispersion measure in [pc*cm^-3]
    :param flow: Lower frequency of FRB in [MHz]
    :param fhigh: Higher frequency of FRB in [MHz]
    """
    # DM formula (1e-3 to change from ms to s)
    td = k*dm*(flow**-2 - fhigh**-2)*1e-3
    return td

if __name__ == '__main__':
    main()
