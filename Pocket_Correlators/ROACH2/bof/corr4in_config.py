# Basic settings
simulated  = False
roach_ip   = '192.168.1.12'
roach_port = 7147
upload     = False
program    = False
boffile    = 'corr4in_2048ch_600mhz.bof.gz'
set_regs   = [{'name' : 'acc_len',    'val' : 2**10}]
reset_regs = ['cnt_rst', 'snap_trig']
bw         = 540.0 # [MHz]

# Snapshot settings
snapshots    = ['adcsnap0', 'adcsnap1', 'adcsnap2', 'adcsnap3']
snap_samples = 256

# Spectrometer Settings
spec_titles   = ['ZDOK0 a', 'ZDOK0 c', 'ZDOK1 a', 'ZDOK1 c']
spec_info     = {'addr_width'  : 9,
                 'word_width'  : 64,
                 'data_type'   : '>u8',
                 'interleave'  : True,
                 'acc_len_reg' : 'acc_len',
                 'bram_names'  : [['dout_0a2_0', 'dout_0a2_1', 'dout_0a2_2', 'dout_0a2_3'],
                                  ['dout_0c2_0', 'dout_0c2_1', 'dout_0c2_2', 'dout_0c2_3'],
                                  ['dout_1a2_0', 'dout_1a2_1', 'dout_1a2_2', 'dout_1a2_3'],
                                  ['dout_1c2_0', 'dout_1c2_1', 'dout_1c2_2', 'dout_1c2_3']]}

# Pocket Correlator Settings 
corr_legends = ['z0c/z0a', 'z1a/z0a', 'z1c/z0a']
crosspow_info = {'addr_width'  : 9,
                 'word_width'  : 64,
                 'data_type'   : '>i8',
                 'interleave'  : True,
                 'acc_len_reg' : 'acc_len',
                 'bram_names'  : [['dout_0a0c_re0', 'dout_0a0c_re1', 'dout_0a0c_re2', 'dout_0a0c_re3'],
                                  ['dout_0a0c_im0', 'dout_0a0c_im1', 'dout_0a0c_im2', 'dout_0a0c_im3'],
                                  ['dout_0a1a_re0', 'dout_0a1a_re1', 'dout_0a1a_re2', 'dout_0a1a_re3'],
                                  ['dout_0a1a_im0', 'dout_0a1a_im1', 'dout_0a1a_im2', 'dout_0a1a_im3'],
                                  ['dout_0a1c_re0', 'dout_0a1c_re1', 'dout_0a1c_re2', 'dout_0a1c_re3'],
                                  ['dout_0a1c_im0', 'dout_0a1c_im1', 'dout_0a1c_im2', 'dout_0a1c_im3']]}

# ADC5G Calibration Settings
snapshots_info = [{'zdok' : 0, 'names' : ['adcsnap0', 'adcsnap1']}, 
                  {'zdok' : 1, 'names' : ['adcsnap2', 'adcsnap3']}]
cal_source = {'type'                : 'visa',
              'connection'          : 'TCPIP::192.168.1.34::INSTR',
              'def_freq'            : 10, # MHz
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
chnl_start = 1
chnl_stop  = 2048
chnl_step  = 32
pause_time = 0.1

# adc synchronator freq settings
sync_chnl_start = 1
sync_chnl_stop  = 200
sync_chnl_step  = 10
sync_regs       = ['adc0_delay', 'adc1_delay', 'adc2_delay', 'adc3_delay']
test_source     = cal_source
lo_sources      = [{'type'       : 'sim',
                    'connection' : 'TCPIP::192.168.1.33::INSTR',
                    'def_freq'   : 3000, # MHz
                    'def_power'  : 19,   # dBm
                    'lo_freqs'   : [0]}] # MHz
