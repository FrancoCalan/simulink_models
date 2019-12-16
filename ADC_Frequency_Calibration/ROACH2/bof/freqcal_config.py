# Basic settings
simulated  = False
roach_ip   = '192.168.1.12'
roach_port = 7147
upload     = True
program    = True
boffile    = 'freqcal2_2048ch_800mhz.bof.gz'
set_regs   = [{'name' : 'acc_len',    'val' : 2**10},
              {'name' : 'filter_gain','val' : 2**27},
              {'name' : 'filter_acc', 'val' : 2**0},
              {'name' : 'channel',    'val' : 1024}]
reset_regs = ['cnt_rst', 'filter_on']
bw         = 540.0 # [MHz]

# Snapshot settings
snapshots    = ['adcsnap0', 'adcsnap1']
snap_samples = 256

# Spectrometer Settings
plot_titles = ['Uncalibrated Spec0', 'Calibrated Spec0', 'Uncalibrated Spec1', 'Calibrated Spec1']
spec_info   = {'addr_width' : 8,
               'word_width' : 64,
               'interleave' : True,
               'data_type'  : '>u8',
               'bram_names' :
               [['dout0_0', 'dout0_1', 'dout0_2', 'dout0_3', 'dout0_4', 'dout0_5', 'dout0_6', 'dout0_7'], 
                ['dout1_0', 'dout1_1', 'dout1_2', 'dout1_3', 'dout1_4', 'dout1_5', 'dout1_6', 'dout1_7'],
                ['dout2_0', 'dout2_1', 'dout2_2', 'dout2_3', 'dout2_4', 'dout2_5', 'dout2_6', 'dout2_7'],
                ['dout3_0', 'dout3_1', 'dout3_2', 'dout3_3', 'dout3_4', 'dout3_5', 'dout3_6', 'dout3_7']]}

# Kestfilt Settings
conv_info_chnl = {'addr_width' : 10,
                  'word_width' : 32,
                  'data_type'  : '>i4',
                  'bram_names' : ['dout_chnl_real1', 'dout_chnl_imag1']}

conv_info_max  = {'addr_width' : 10,
                  'word_width' : 64,
                  'data_type'  : '>u8',
                  'bram_names' : 'dout_chnl_max0'}

conv_info_mean = {'addr_width' : 10,
                  'word_width' : 64,
                  'data_type'  : '>u8',
                  'bram_names' : 'dout_chnl_mean0'}

###
inst_chnl_info = {'addr_width' : 10,
                  'word_width' : 32,
                  'data_type'  : '>i4',
                  'bram_names' : [['dout_chnl_real1', 'dout_chnl_imag1'],
                                  ['dout_chnl_real0', 'dout_chnl_imag0']]}
