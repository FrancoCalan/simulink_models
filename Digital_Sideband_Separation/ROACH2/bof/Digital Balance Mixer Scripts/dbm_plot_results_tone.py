import tarfile, json
import numpy as np
import matplotlib.pyplot as plt

# file names
ideal_file = 'dbm_lnr_tone 2020-02-27 17:48:47.tar.gz'
cal_file   = 'dbm_lnr_tone 2020-02-27 17:53:45.tar.gz'

def main():
    # get data
    ifreqs_usb, ifreqs_lsb, ilnr_usb, ilnr_lsb = get_lnrdata(ideal_file)
    cfreqs_usb, cfreqs_lsb, clnr_usb, clnr_lsb = get_lnrdata(cal_file)
    
    # plot data
    plt.plot(ifreqs_usb, 10*np.log10(ilnr_usb), 'b', label='ideal')
    plt.plot(ifreqs_lsb, 10*np.log10(ilnr_lsb), 'b')
    plt.plot(cfreqs_usb, 10*np.log10(clnr_usb), 'r', label='calibrated')
    plt.plot(cfreqs_lsb, 10*np.log10(clnr_lsb), 'r')
    plt.grid()
    plt.xlabel('Frequency [MHz]')
    plt.ylabel('LNR [dB]')
    plt.legend()
    plt.show()

def get_lnrdata(lnrfile):
    # extract data
    tar_file = tarfile.open(lnrfile)
    lnrdata =np.load(tar_file.extractfile('lnrdata.npz'))
    testinfo = json.load(tar_file.extractfile('testinfo.json'))

    # get freq data
    lofreq    = testinfo["lo freq"]
    bandwidth = testinfo["bandwidth"]
    nchannels = testinfo["nchannels"]
    
    # compute freqs
    if_freqs = np.linspace(0, bandwidth, nchannels, endpoint=False)
    freqs_usb = lofreq + if_freqs
    freqs_lsb = lofreq - if_freqs

    # get lnr data
    rf_toneusb = lnrdata['rf_toneusb']; lo_toneusb = lnrdata['lo_toneusb']
    rf_tonelsb = lnrdata['rf_tonelsb']; lo_tonelsb = lnrdata['lo_tonelsb']

    # compute ratios
    lnr_usb = lo_toneusb / rf_toneusb
    lnr_lsb = lo_tonelsb / rf_tonelsb

    return freqs_usb, freqs_lsb, lnr_usb, lnr_lsb

if __name__ == '__main__':
    main()
