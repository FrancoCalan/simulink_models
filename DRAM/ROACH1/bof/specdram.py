#!/usr/bin/python
# Script to plot an spectrogram from a specdram model.
# Spectrogram data is read from DRAM memory

# imports
import time
import calandigital as cd
import numpy as np
import matplotlib.pyplot as plt

# communication parameters
roach_ip = "192.168.1.11"
roach_port = 7147
boffile = "specdram_4096ch_500mhz.bof"

# model parameters
bandwidth       = 480.0 # MMz
dram_addr_width = 22
dram_word_width = 128   # bits
dram_data_type  = '>u4'
nchannels       = 4096

# derivative parameters
freqs      = np.linspace(0, bandwidth, nchannels, endpoint=False)
dBFS       = 6.02*8 + 1.76 + 10*np.log10(nchannels/2) # Hard-coded 8-bits ADC
data_nbits = np.dtype(dram_data_type).alignment * 8
ndata      = 2**dram_addr_width * dram_word_width / data_nbits
nspecs     = ndata / nchannels
Ts         = 1/(2*bandwidth) / 1000 # ms
spectime   = Ts * nchannels
extent     = [0, spectime * nspecs, 0, bandwidth]

def main():
    # initialize roach
    roach = cd.initialize_roach(roach_ip, boffile=boffile, timeout=120)
    time.sleep(1)

    # create figure
    img, cbar = create_colormap_fig(extent)

    # get spectrogram data
    print("Getting DRAM data...")
    specgram_data = get_dram_spectrogram_data(roach, 
        dram_addr_width, dram_word_width, dram_data_type)
    print("done")

    # plot spectrogram 
    img.set_data(specgram_data)
    img.set_clim(vmin=np.min(specgram_data), vmax=np.max(specgram_data))
    cbar.update_normal(img)
    plt.show()

def create_colormap_fig(extent):
    """
    Creates figure and image to plot a colormap.
    """
    fig  = plt.figure()
    ax   = fig.gca()
    img  = ax.imshow([[0,0],[0,0]], origin='lower', aspect='auto', 
        interpolation='spline36', extent=extent)
    cbar = fig.colorbar(img)

    ax.set_xlabel('Time [ms]')
    ax.set_ylabel('Frequency [MHz]')
    cbar.set_label("Power [dB]")

    return img, cbar

def get_dram_spectrogram_data(roach, addr_width, data_width, dtype):
    """
    Get spectrogram data from DRAM.
    :param roach: CalanFpga object.
    :param addr_width: address width in bits.
    :param data_width: data width in bits.
    :param dtype: data type of dram data.
    :return: spectrogram data in dBFS.
    """
    specgram_data = cd.read_dram_data(roach, addr_width, data_width, dtype)
    specgram_data = specgram_data.reshape(nchannels, nspecs) # convert spectrogram data into a time x freq matrix
    specgram_data = np.transpose(specgram_data) # rotate matrix to have freq in y axis, and time in x axis
    specgram_data = cd.scale_and_dBFS_specdata(specgram_data, 1, dBFS) # convert data to dBFS
    
    return specgram_data

if __name__ == '__main__':
    main()
