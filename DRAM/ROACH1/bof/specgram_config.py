# Basic settings
simulated  = False
roach_ip   = '192.168.1.11'
roach_port = 7147
upload     = False
program    = True
boffile    = 'specdram_4096ch_500mhz.bof'
set_regs   = [{'name' : 'acc_len', 'val' : 2**10}]
reset_regs = ['cnt_rst']
bw         = 480.0 # [MHz]

# Snapshot settings
snapshots    = ['adcsnap0']
snap_samples = 256

# Spectrometer settings
plot_titles = ['ZDOK0']
spec_info   = {'addr_width'  : 10,
               'word_width'  : 64,
               'data_type'   : '>u8',
               'interleave'  : True,
               'acc_len_reg' : 'acc_len',
               'bram_names'  :
               ['dout0_0', 'dout0_1', 'dout0_2', 'dout0_3']}

# Spectrogram settings
specgram_info = {'addr_width' : 22,
                 'word_width' : 128,
                 'data_type'  : '>i4',
                 'n_channels' : 4096}
