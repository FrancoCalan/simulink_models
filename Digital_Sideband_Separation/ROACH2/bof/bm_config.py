# Basic settings
simulated  = False
roach_ip   = '192.168.1.12'
roach_port = 7147
upload     = False
program    = False
boffile    = 'dss_2048ch_1080mhz.bof.gz'
set_regs   = [{'name' : 'syn_acc_len',    'val' : 2**20},
              {'name' : 'cal_acc_len',    'val' : 2**20}]
reset_regs = ['cnt_rst', 'snap_trig']
bw         = 1080.0 # [MHz]

# Snapshot settings
snapshots    = ['adcsnap0', 'adcsnap1']
snap_samples = 256

# adc5g calibration settings
snapshots_info = [{'zdok' : 0, 'names' : ['adcsnap0']}, 
                  {'zdok' : 1, 'names' : ['adcsnap1']}]
cal_source     =  {'type'        : 'sim',
                   'connection'  : 'TCPIP::192.168.1.34::INSTR',
                   'def_freq'    :  10, # MHz
                   'def_power'   : -10} # dBm
do_mmcm        = True
do_ogp         = False
do_inl         = False
load_ogp       = True
load_inl       = True
plot_snapshots = False
plot_spectra   = False
caldir         = ""
loaddir        = 'calibrations_2019-06-06 14:59:31'

# ADC Synchronization Freq settings
sync_chnl_start = 1
sync_chnl_stop  = 700
sync_chnl_step  = 10
sync_regs       = ['adc1_delay', 'adc0_delay']    
test_source     =  {'type'       : 'sim',
                   'connection'  : 'TCPIP::192.168.1.34::INSTR',
                   'def_freq'    :  10, # MHz
                   'def_power'   : -10} # dBm
lo_source       = {'type'       : 'sim',
                   'connection' : 'TCPIP::192.168.1.33::INSTR',
                   'def_freq'   : 10,      # MHz
                   'def_power'  : 10,      # dBm
                   'lo_freq'    : 2400}    # MHz
lo_sources      = [{'type'       : 'sim',
                   'connection' : 'TCPIP::192.168.1.33::INSTR',
                   'def_freq'   : 10,      # MHz
                   'def_power'  : 10,      # dBm
                   'lo_freqs'   : [2400]}] # MHz

pause_time      = 1e-10
spec_info = {'addr_width'  : 8,
             'word_width'  : 64,
             'data_type'   : '>u8',
             'interleave'  : True,
             'acc_len_reg' : 'cal_acc_len',
             'bram_names'  :
             [['dout_a2_0', 'dout_a2_1', 'dout_a2_2', 'dout_a2_3', 'dout_a2_4', 'dout_a2_5', 'dout_a2_6', 'dout_a2_7'],
              ['dout_b2_0', 'dout_b2_1', 'dout_b2_2', 'dout_b2_3', 'dout_b2_4', 'dout_b2_5', 'dout_b2_6', 'dout_b2_7']]}
             
crosspow_info = {'addr_width'  : 8,
                 'word_width'  : 64,
                 'data_type'   : '>i8',
                 'interleave'  : True,
                 'acc_len_reg' : 'cal_acc_len',
                 'bram_names'  :
                 [['dout_ab_re0', 'dout_ab_re1', 'dout_ab_re2', 'dout_ab_re3', 'dout_ab_re4', 'dout_ab_re5', 'dout_ab_re6', 'dout_ab_re7'],
                  ['dout_ab_im0', 'dout_ab_im1', 'dout_ab_im2', 'dout_ab_im3', 'dout_ab_im4', 'dout_ab_im5', 'dout_ab_im6', 'dout_ab_im7']]}

# BM settings
cal_chnl_step        = 8
syn_chnl_start       = 1
syn_chnl_stop        = 700 
syn_chnl_step        = 8
compute_cancellation = True
rf_source            = test_source

const_bin_pt = 27 # 32_27
const_brams_info = {'addr_width'      : 8,
                    'word_width'      : 32,
                    'data_type'       : '>i4',
                    'deinterleave_by' : 8,
                    'bram_names'      :
                    [['bram_mult0_0_bram_re', 'bram_mult0_1_bram_re', 'bram_mult0_2_bram_re', 'bram_mult0_3_bram_re', 
                      'bram_mult0_4_bram_re', 'bram_mult0_5_bram_re', 'bram_mult0_6_bram_re', 'bram_mult0_7_bram_re'],
                     ['bram_mult0_0_bram_im', 'bram_mult0_1_bram_im', 'bram_mult0_2_bram_im', 'bram_mult0_3_bram_im', 
                      'bram_mult0_4_bram_im', 'bram_mult0_5_bram_im', 'bram_mult0_6_bram_im', 'bram_mult0_7_bram_im']]}

synth_info   = {'addr_width'  : 8,
                'word_width'  : 64,
                'data_type'   : '>u8',
                'interleave'  : True,
                'acc_len_reg' : 'syn_acc_len',
                'bram_names'  :
                ['dout0_0', 'dout0_1', 'dout0_2', 'dout0_3', 'dout0_4', 'dout0_5', 'dout0_6', 'dout0_7']}
synth_titles = ['synth spec']
do_digital = True
do_analog  = True

# spectra settings
spec_titles = ['ZDOK0', 'ZDOK1']

# pocket correlator settings
corr_legends = ['z1/z0']
chnl_start  = 1
chnl_stop   = 2048
chnl_step   = 8
