# Basic settings
simulated  = False
roach_ip   = '192.168.1.12'
roach_port = 7147
upload     = True
program    = True
boffile    = 'corr2in_4096ch_1080mhz.bof.gz'
set_regs   = [{'name' : 'acc_len',    'val' : 2**10}]
reset_regs = ['cnt_rst', 'snap_trig']
bw         = 1080.0 # [MHz]

# Snapshot settings
snapshots    = ['adcsnap0', 'adcsnap1']
snap_samples = 256

# Spectrometer Settings
spec_titles   = ['ZDOK0', 'ZDOK1']
spec_info     = {'addr_width'  : 9,
                 'word_width'  : 64,
                 'data_type'   : '>u8',
                 'interleave'  : True,
                 'acc_len_reg' : 'acc_len',
                 'bram_names'  : [['dout_a2_0', 'dout_a2_1', 'dout_a2_2', 'dout_a2_3', 'dout_a2_4', 'dout_a2_5', 'dout_a2_6', 'dout_a2_7'],
                                  ['dout_b2_0', 'dout_b2_1', 'dout_b2_2', 'dout_b2_3', 'dout_b2_4', 'dout_b2_5', 'dout_b2_6', 'dout_b2_7']]}

# Pocket Correlator Settings 
corr_legends = ['z1/z0']
crosspow_info = {'addr_width'  : 9,
                 'word_width'  : 64,
                 'data_type'   : '>i8',
                 'interleave'  : True,
                 'acc_len_reg' : 'acc_len',
                 'bram_names'  : [['dout_ab_re0', 'dout_ab_re1', 'dout_ab_re2', 'dout_ab_re3', 'dout_ab_re4', 'dout_ab_re5', 'dout_ab_re6', 'dout_ab_re7'],
                                  ['dout_ab_im0', 'dout_ab_im1', 'dout_ab_im2', 'dout_ab_im3', 'dout_ab_im4', 'dout_ab_im5', 'dout_ab_im6', 'dout_ab_im7']]}

# ADC5G Calibration Settings
snapshots_info = [{'zdok' : 0, 'names' : ['adcsnap0']},
                  {'zdok' : 1, 'names' : ['adcsnap1']}]
cal_source = {'type'                : 'visa',
              'connection'          : 'TCPIP::192.168.1.34::INSTR',
              'def_freq'            : 10,  # MHz
              'def_power'           : -10} # dBm
do_mmcm        = True
do_ogp         = False
do_inl         = False
load_ogp       = True
load_inl       = True
plot_snapshots = False
plot_spectra   = False
caldir         = 'calibrations'
loaddir        = '../../../Spectrometers/ROACH2/bof/calibrations_2019-06-06 14:59:31'

# frequency response settings
test_source = cal_source
chnl_start  = 1
chnl_stop   = 4096
chnl_step   = 32
pause_time  = 0.1

# adc synchronator freq settings
sync_chnl_start   = 1
sync_chnl_stop    = 100
sync_chnl_step    = 10
sync_regs         = ['adc1_delay', 'adc0_delay'] 
lo_sources        = [{'type'       : 'sim',
                      'connection' : 'TCPIP::192.168.1.33::INSTR',
                      'def_freq'   : 3000,    # MHz
                      'def_power'  : 19,      # dBm
                      'lo_freqs'   : [0]}] # MHz
