# Basic settings
simulated  = False
roach_ip   = '192.168.1.15'
roach_port = 7147
upload     = True
program    = True
boffile    = 'spec2in_4096ch_1080mhz.bof.gz'
set_regs   = [{'name' : 'acc_len', 'val' : 2**10}]
reset_regs = ['cnt_rst']
bw         = 1000.0 # [MHz]

# Snapshot settings
snapshots    = ['adcsnap0', 'adcsnap1']
snap_samples = 256

# Spectrometer settings
spec_titles = ['ZDOK0', 'ZDOK1']
spec_info   = {'addr_width'  : 9,
               'word_width'  : 64,
               'data_type'   : '>u8',
               'interleave'  : True,
               'acc_len_reg' : 'acc_len',
               'bram_names'  :
               [['dout0_0', 'dout0_1', 'dout0_2', 'dout0_3', 'dout0_4', 'dout0_5', 'dout0_6', 'dout0_7'], 
                ['dout1_0', 'dout1_1', 'dout1_2', 'dout1_3', 'dout1_4', 'dout1_5', 'dout1_6', 'dout1_7']]}

# adc5g calibration settings
snapshots_info = [{'zdok' : 0, 'names' : ['adcsnap0']},
                  {'zdok' : 1, 'names' : ['adcsnap1']}]
cal_source = {'type'                : 'scpi',
              'connection'          : 'TCPIP::192.168.1.33::INSTR',
              'def_freq'            : 10, # MHz
              'def_power'           : -5}  # dBm
do_mmcm        = True
do_ogp         = True
do_inl         = True
load_ogp       = False
load_inl       = False
plot_snapshots = True
plot_spectra   = True
caldir         = 'calibrations'
loaddir        = 'calibrations_2019-06-06 14:59:31'

# frequency response settings
test_source = cal_source
chnl_start = 1
chnl_stop  = 2048
chnl_step = 8
pause_time = 0.1

# adc synchronator freq settings
sync_chnl_start = 1
sync_chnl_stop  = 200
sync_chnl_step  = 10
sync_regs       = ['adc0_delay', 'adc1_delay']
test_source     = cal_source
lo_sources      = [{'type'       : 'sim',
                    'connection' : 'TCPIP::192.168.1.33::INSTR',
                    'def_freq'   : 3000, # MHz
                    'def_power'  : 19,   # dBm
                    'lo_freqs'   : [0]}] # MHz
