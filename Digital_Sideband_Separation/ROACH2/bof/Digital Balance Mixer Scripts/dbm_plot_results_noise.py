import tarfile, json
import numpy as np
import matplotlib.pyplot as plt

# file names
ideal_file = 'dbm_lnr_noise 2020-02-28 19:33:19.tar.gz'
cal_file   = 'dbm_lnr_noise 2020-02-28 19:35:51.tar.gz'

def main():
    # get data
    ifreqs, ilnr = get_lnrdata(ideal_file)
    cfreqs, clnr = get_lnrdata(cal_file)
    
    # plot data
    plt.plot(ifreqs, 10*np.log10(ilnr), 'b', label='ideal')
    plt.plot(cfreqs, 10*np.log10(clnr), 'r', label='calibrated')
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
    rf_freqs = lofreq + if_freqs

    # get lnr data
    rf_cold = lnrdata['rf_cold']; lo_cold = lnrdata['lo_cold']
    rf_hot  = lnrdata['rf_hot'];  lo_hot  = lnrdata['lo_hot']

    # compute lnr
    lnr = (rf_hot - rf_cold) / (lo_hot - lo_cold) + 1

    return rf_freqs, lnr

if __name__ == '__main__':
    main()
