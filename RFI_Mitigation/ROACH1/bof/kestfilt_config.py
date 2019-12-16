# Basic settings
simulated  = False
roach_ip   = '192.168.1.11'
roach_port = 7147
upload     = False
program    = True
#boffile    = 'kestfilt_2048ch_60mhz.bof'
#boffile    = 'kestfilt_60mhz_fm.bof'
boffile    = 'kestfilt_60mhz_hline.bof'
set_regs   = [{'name' : 'acc_len',     'val' : 2**16},
              {'name' : 'filter_gain', 'val' : 2**32-1},
              {'name' : 'filter_acc',  'val' : 1},
              {'name' : 'channel',     'val' : 1570}] # 46[MHz]
reset_regs = ['cnt_rst', 'filter_on']
bw         = 60.0 # [MHz]

# Snapshot settings
snapshots    = ['adcsnap0', 'adcsnap1']
snap_samples = 256

# Spectrometer Settings
plot_titles = ['Primary Signal', 'Reference Signal', 'Filter Output']
#plot_titles = ['Primary Signal', 'Reference Signal']
#plot_titles = ['Primary Signal']
spec_info   = {'addr_width'  : 11,
               'word_width'  : 64,
               'data_type'   : '>u8',
               'acc_len_reg' : 'acc_len',
               'bram_names'  : ['dout0_0', 'dout1_0', 'dout2_0']}

# Kestfilt Settings
conv_info_chnl = {'addr_width' : 10,
                  'word_width' : 32,
                  'data_type'  : '>i4',
                  'bram_names' : ['dout_chnl_real2', 'dout_chnl_imag2']}

conv_info_max  = {'addr_width' : 10,
                  'word_width' : 64,
                  'data_type'  : '>u8',
                  'bram_names' : 'dout_chnl_max'}

conv_info_mean = {'addr_width' : 10,
                  'word_width' : 64,
                  'data_type'  : '>u8',
                  'bram_names' : 'dout_chnl_mean'}
###
inst_chnl_info = {'addr_width' : 10,
                  'word_width' : 32,
                  'data_type'  : '>i4',
                  'bram_names' : [['dout_chnl_real0', 'dout_chnl_imag0'],
                                  ['dout_chnl_real1', 'dout_chnl_imag1']]}
