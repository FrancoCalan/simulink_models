# Basic settings
simulated  = False
roach_ip   = '192.168.1.12'
roach_port = 7147
upload     = False
program    = False
boffile    = 'spec4in_2048ch_600mhz.bof.gz'
set_regs   = [{'name' : 'acc_len', 'val' : 2**10}]
reset_regs = ['cnt_rst']
bw         = 500.0 # [MHz]

# Snapshot settings
#snapshots    = ['adcsnap0', 'adcsnap1']
snapshots    = ['adcsnap0', 'adcsnap1', 'adcsnap2', 'adcsnap3']
snap_samples = 256

# Spectrometer settings
spec_titles = ['ZDOK0 a', 'ZDOK0 c', 'ZDOK1 a', 'ZDOK1 c']
spec_info   = {'addr_width'  : 9,
               'word_width'  : 64,
               'data_type'   : '>u8',
               'interleave'  : True,
               'acc_len_reg' : 'acc_len',
               'bram_names'  :
               [['pow_0a_0', 'pow_0a_1', 'pow_0a_2', 'pow_0a_3'],
                ['pow_0c_0', 'pow_0c_1', 'pow_0c_2', 'pow_0c_3'],
                ['pow_1a_0', 'pow_1a_1', 'pow_1a_2', 'pow_1a_3'],
                ['pow_1c_0', 'pow_1c_1', 'pow_1c_2', 'pow_1c_3']]}

# adc5g calibration settings
snapshots_info = [{'zdok' : 0, 'names' : ['adcsnap0', 'adcsnap1']}, 
                  {'zdok' : 1, 'names' : ['adcsnap2', 'adcsnap3']}]
cal_source = {'type'                : 'visa',
              'connection'          : 'TCPIP::192.168.1.33::INSTR',
              'def_freq'            : 10, # MHz
              'def_power'           : 0} # dBm
do_mmcm        = True
do_ogp         = False
do_inl         = False
load_ogp       = True
load_inl       = True
plot_snapshots = False
plot_spectra   = False
caldir         = 'calibrations'
loaddir        = 'calibrations_2018-12-18 19:09:38'

# frequency response settings
test_source = cal_source
chnl_start = 1
chnl_stop  = 2048
chnl_step = 64
pause_time = 0.1
