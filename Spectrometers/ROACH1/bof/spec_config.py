# Basic settings
simulated  = False
roach_ip   = '192.168.1.11'
roach_port = 7147
upload     = False
program    = True
boffile    = 'spec2in_4096ch_500mhz.bof'
set_regs   = [{'name' : 'acc_len', 'val' : 2**10}]
reset_regs = ['cnt_rst']
bw          = 500 # [MHz]

# Snapshot settings
snapshots    = ['adcsnap0', 'adcsnap1']
snap_samples = 256

# Spectrometer Settings
spec_titles = ['ZDOK0', 'ZDOK1']
spec_info   = {'addr_width'  : 10,
               'word_width'  : 64,
               'data_type'   : '>u8',
               'interleave'  : True,
               'acc_len_reg' : 'acc_len',
               'bram_names'  :
               [['dout0_0', 'dout0_1', 'dout0_2', 'dout0_3'],
                ['dout1_0', 'dout1_1', 'dout1_2', 'dout1_3']]}
