# Basic settings
simulated  = False
roach_ip   = '192.168.1.12'
roach_port = 7147
upload     = False
program    = False
boffile    = 'dss_2048ch_1080mhz.bof.gz'
set_regs   = [{'name' : 'syn_acc_len',    'val' : 2**10},
              {'name' : 'cal_acc_len',    'val' : 2**10}]
reset_regs = ['cnt_rst', 'snap_trig']
bw         = 1000.0 # [MHz]

# Snapshot settings
snapshots    = ['adcsnap0', 'adcsnap1']
snap_samples = 256

# adc5g calibration settings
snapshots_info = [{'zdok' : 0, 'names' : ['adcsnap0']}, 
                  {'zdok' : 1, 'names' : ['adcsnap1']}]
cal_source     =  {'type'        : 'sim',
                   'connection'  : 'TCPIP::192.168.1.34::INSTR',
                   'def_freq'    : 10, # MHz
                   'def_power'   : -3} # dBm
do_mmcm        = True
do_ogp         = False
do_inl         = False
load_ogp       = True
load_inl       = True
plot_snapshots = False
plot_spectra   = False
caldir         = ""
loaddir        = '../../../Spectrometers/ROACH2/bof/calibrations_2018-12-18 19:09:38'

# ADC Synchronization Freq settings
sync_chnl_start = 1
sync_chnl_stop  = 101
sync_chnl_step  = 10
test_source       = {'type'       : 'visa',
                     'connection' : 'TCPIP::192.168.1.34::INSTR',
                     'def_freq'   : 10, # MHz
                     'def_power'  : -18} # dBm

lo_sources      = [{'type'       : 'visa',
                    'connection' : 'TCPIP::192.168.1.33::INSTR',
                    'def_freq'   : 3000,    # MHz
                    'def_power'  : 19,      # dBm
                    'lo_freqs'   : [3000]}] # MHz
pause_time      = 1e-10
specsync_info = {'addr_width'  : 8,
                 'word_width'  : 64,
                 'data_type'   : '>u8',
                 'interleave'  : True,
                 'acc_len_reg' : 'cal_acc_len',
                 'bram_names'  :
                 [['dout_a2_0', 'dout_a2_1', 'dout_a2_2', 'dout_a2_3', 'dout_a2_4', 'dout_a2_5', 'dout_a2_6', 'dout_a2_7'],
                  ['dout_b2_0', 'dout_b2_1', 'dout_b2_2', 'dout_b2_3', 'dout_b2_4', 'dout_b2_5', 'dout_b2_6', 'dout_b2_7']]}
             
crosspowsync_info = {'addr_width'  : 8,
                     'word_width'  : 64,
                     'data_type'   : '>i8',
                     'interleave'  : True,
                     'acc_len_reg' : 'cal_acc_len',
                     'bram_names'  :
                     [['dout_ab_re0', 'dout_ab_re1', 'dout_ab_re2', 'dout_ab_re3', 'dout_ab_re4', 'dout_ab_re5', 'dout_ab_re6', 'dout_ab_re7'],
                      ['dout_ab_im0', 'dout_ab_im1', 'dout_ab_im2', 'dout_ab_im3', 'dout_ab_im4', 'dout_ab_im5', 'dout_ab_im6', 'dout_ab_im7']]}

# DSS settings
kerr_correction = False
ideal_consts    = {'load' : False, 'val' : 0+1j}
cal_chnl_step   = 128
srr_chnl_step   = 128
rf_source       = test_source

spec_info = specsync_info
crosspow_info = crosspowsync_info
const_bin_pt = 27 # 32_27
const_brams_info = {'addr_width'      : 8,
                    'word_width'      : 32,
                    'data_type'       : '>i4',
                    'deinterleave_by' : 8,
                    'bram_names'      :
                    [['bram_mult0_0_bram_re', 'bram_mult0_1_bram_re', 'bram_mult0_2_bram_re', 'bram_mult0_3_bram_re', 
                      'bram_mult0_4_bram_re', 'bram_mult0_5_bram_re', 'bram_mult0_6_bram_re', 'bram_mult0_7_bram_re'],
                     ['bram_mult0_0_bram_im', 'bram_mult0_1_bram_im', 'bram_mult0_2_bram_im', 'bram_mult0_3_bram_im', 
                      'bram_mult0_4_bram_im', 'bram_mult0_5_bram_im', 'bram_mult0_6_bram_im', 'bram_mult0_7_bram_im'],
                     ['bram_mult1_0_bram_re', 'bram_mult1_1_bram_re', 'bram_mult1_2_bram_re', 'bram_mult1_3_bram_re', 
                      'bram_mult1_4_bram_re', 'bram_mult1_5_bram_re', 'bram_mult1_6_bram_re', 'bram_mult1_7_bram_re'],
                     ['bram_mult1_0_bram_im', 'bram_mult1_1_bram_im', 'bram_mult1_2_bram_im', 'bram_mult1_3_bram_im', 
                      'bram_mult1_4_bram_im', 'bram_mult1_5_bram_im', 'bram_mult1_6_bram_im', 'bram_mult1_7_bram_im']]}

synth_info   = {'addr_width'  : 8,
                'word_width'  : 64,
                'data_type'   : '>u8',
                'interleave'  : True,
                'acc_len_reg' : 'syn_acc_len',
                'bram_names'  :
                [['dout0_0', 'dout0_1', 'dout0_2', 'dout0_3', 'dout0_4', 'dout0_5', 'dout0_6', 'dout0_7'], 
                 ['dout1_0', 'dout1_1', 'dout1_2', 'dout1_3', 'dout1_4', 'dout1_5', 'dout1_6', 'dout1_7']]}

# spectra settings
spec_titles = ['ZDOK0', 'ZDOK1']
