# Basic settings
simulated  = False
roach_ip   = '192.168.1.12'
roach_port = 7147
upload     = False
program    = False
boffile    = 'mcs_1mch_70mhz2.bof.gz'
set_regs   = [{'name' : 'acc_len',  'val' : 2**10},]
#              {'name' : 'band_sel', 'val' : 0}]
reset_regs = ['cnt_rst']
bw         = 4.21875 # [MHz]
#qdr        = 'qdr0'

# Snapshot settings
snapshots    = ['adcsnap0']
snap_samples = 256

# Spectrometer settings
spec_titles = ['ZDOK0']
spec_info   = {'addr_width'  : 8,
               'word_width'  : 64,
               'data_type'   : '>u8',
               'interleave'  : False,
               'acc_len_reg' : 'acc_len',
               'bram_names'  : 'dout1_0'}
#spec_info   = {'addr_width'  : 16,
#               'word_width'  : 64,
#               'data_type'   : '>u8',
#               'interleave'  : False,
#               'acc_len_reg' : 'acc_len',
#               'bram_names'  : 'dout2_0'}

# adc5g calibration settings
snapshots_info = [{'zdok' : 0, 'names' : ['adcsnap0']},]
cal_source = {'type'                : 'scpi',
              'connection'          : 'TCPIP::192.168.1.33::INSTR',
              'def_freq'            : 10, # MHz
              'def_power'           : -5}  # dBm
do_mmcm        = True
do_ogp         = False
do_inl         = False
load_ogp       = True
load_inl       = True
plot_snapshots = False
plot_spectra   = False
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
