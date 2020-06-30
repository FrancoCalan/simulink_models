import corr, time
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# parameters
roachip   = "192.168.0.11"
boffile   = "spec_compare.bof.gz"
bandwidth = 100 # MHz
fftsize   = 1024
brams     = ["dout0", "dout"]
dtypename = ">u8"
#dtypename = np.uint64

freqs     = np.linspace(0, bandwidth, fftsize, endpoint=False)
dBFS      = 6.02*8 + 1.76 + 10*np.log10(fftsize) # 8 bits
dtype     = np.dtype(dtypename)

def main():
    roach = initialize_roach()
    #roach = DummyRoach()
    fig, lines = create_figure()

    # animation definition
    def animate(_):
        for line, bram in zip(lines, brams):
            data = read_data(roach, bram)
            data = process_data(data)
            line.set_data(freqs, data)
        return lines

    # create animation
    ani = FuncAnimation(fig, animate, blit=True)
    plt.show()

def initialize_roach():
    roach = corr.katcp_wrapper.FpgaClient(roachip)
    time.sleep(0.5)
    roach.upload_program_bof(boffile, 60000)
    time.sleep(1)
    return roach

def create_figure():
    fig, axes = plt.subplots(1, 2)
    fig.set_tight_layout(True)

    lines = []
    for ax in axes:
        ax.set_xlim(0, bandwidth)
        ax.set_ylim(-dBFS-2, 0)
        ax.set_xlabel("Frequency [MHz]")
        ax.set_ylabel("Power [dBFS]")
        ax.grid()

        line, = ax.plot([], [], animated=True)
        lines.append(line)

    axes[0].set_title("Xilinx FFT")
    axes[1].set_title("My FFT")

    return fig, lines

def read_data(roach, bram):
    wordbytes = dtype.alignment
    rawdata = roach.read(bram, fftsize*wordbytes, 0)
    bramdata = np.frombuffer(rawdata, dtype=dtype)

    return bramdata

def process_data(data):
    # convert data into dBFS
    data = 10*np.log10(data+1) - dBFS

    # reorder data into canonical order
    for i in range(len(data)):
        j = reverse_bits(i, int(np.log2(fftsize)))
        if i < j:
            temp    = data[i]
            data[i] = data[j]
            data[j] = temp
    return data

def reverse_bits(x, nbits):
    y = 0
    for _ in range(nbits):
        y = (y << 1) + (x & 1)
        x >>= 1
    return int(y)

class DummyRoach():
    def __init__(self):
        pass
    def read(self, bram, nbytes, offset):
        #data = np.full(fftsize, 1023, dtype=dtype)
        #data = np.arange(fftsize, dtype=dtype)
        data = np.random.randint(0, 10000000, fftsize, dtype=dtype)
        return data.tobytes()

if __name__ == '__main__':
    main()
