# Basic settings
simulated  = False
roach_ip   = '192.168.1.12'
roach_port = 7147
upload     = False
program    = False
boffile    = 'domt_2048ch_600mhz.bof.gz'
set_regs   = [{'name' : 'syn_acc_len', 'val' : 2**10},
              {'name' : 'cal_acc_len', 'val' : 2**10},
              {'name' : 'ref_select',  'val' : 0}] # ref=0 to perform synchronization
reset_regs = ['cnt_rst', 'snap_trig']
bw         = 540.0 # [MHz]

# Snapshot settings
snapshots    = ['adcsnap0', 'adcsnap1', 'adcsnap2', 'adcsnap3']
snap_samples = 256

# adc5g calibration settings
snapshots_info = [{'zdok' : 0, 'names' : ['adcsnap0', 'adcsnap1']}, 
                  {'zdok' : 1, 'names' : ['adcsnap2', 'adcsnap3']}]
cal_source     =  {'type'        : 'sim',
                   'connection'  : 'TCPIP::192.168.1.34::INSTR',
                   'def_freq'    : 10, # MHz
                   'def_power'   : -3} # dBm
do_mmcm        = True
do_ogp         = False
do_inl         = False
load_ogp       = False
load_inl       = True
plot_snapshots = False
plot_spectra   = False
caldir         = ""
loaddir        = '../../../Spectrometers/ROACH2/bof/calibrations_2019-06-06 14:59:31'

# ADC Synchronization Freq settings
sync_chnl_start = 1
sync_chnl_stop  = 1001
sync_chnl_step  = 50
sync_regs       = ['adc0_delay', 'adc1_delay', 'adc2_delay', 'adc3_delay']
test_source      = {'type'       : 'scpi',
                    'connection' : 'TCPIP::192.168.1.31::INSTR',
                    'def_freq'   : 10, # MHz
                    'def_power'  : -11} # dBm

lo_sources      = [{'type'       : 'scpi',
                    'connection' : 'TCPIP::192.168.1.36::INSTR',
                    'def_freq'   : 12000,    # MHz
                    'def_power'  : 25.5,     # dBm
                    'lo_freqs'   : [12000]}] # MHz
pause_time      = 1e-10

# DOMT settings
ideal_consts      = True
calibration_45deg = False
cal_chnl_step     = 128
syn_chnl_step     = 128
rf_source         = test_source

spec_info = {'addr_width'  : 9,
             'word_width'  : 64,
             'data_type'   : '>u8',
             'interleave'  : True,
             'acc_len_reg' : 'cal_acc_len',
             'bram_names'  :
             [['dout_0a2_0', 'dout_0a2_1', 'dout_0a2_2', 'dout_0a2_3'],
              ['dout_0c2_0', 'dout_0c2_1', 'dout_0c2_2', 'dout_0c2_3'],
              ['dout_1a2_0', 'dout_1a2_1', 'dout_1a2_2', 'dout_1a2_3'],
              ['dout_1c2_0', 'dout_1c2_1', 'dout_1c2_2', 'dout_1c2_3']]}
crosspow_info = {'addr_width'  : 9,
                 'word_width'  : 64,
                 'data_type'   : '>i8',
                 'interleave'  : True,
                 'acc_len_reg' : 'cal_acc_len',
                 'bram_names'  :
                 [['dout_0a_ref_re0', 'dout_0a_ref_re1', 'dout_0a_ref_re2', 'dout_0a_ref_re3'],
                  ['dout_0a_ref_im0', 'dout_0a_ref_im1', 'dout_0a_ref_im2', 'dout_0a_ref_im3'],
                  ['dout_0c_ref_re0', 'dout_0c_ref_re1', 'dout_0c_ref_re2', 'dout_0c_ref_re3'],
                  ['dout_0c_ref_im0', 'dout_0c_ref_im1', 'dout_0c_ref_im2', 'dout_0c_ref_im3'],
                  ['dout_1a_ref_re0', 'dout_1a_ref_re1', 'dout_1a_ref_re2', 'dout_1a_ref_re3'],
                  ['dout_1a_ref_im0', 'dout_1a_ref_im1', 'dout_1a_ref_im2', 'dout_1a_ref_im3'],
                  ['dout_1c_ref_re0', 'dout_1c_ref_re1', 'dout_1c_ref_re2', 'dout_1c_ref_re3'],
                  ['dout_1c_ref_im0', 'dout_1c_ref_im1', 'dout_1c_ref_im2', 'dout_1c_ref_im3']]}

const_bin_pt = 1 # 32_27
const_brams_info = {'addr_width'      : 9,
                    'word_width'      : 32,
                    'data_type'       : '>i4',
                    'deinterleave_by' : 4,
                    'bram_names'      :
                    [[[['consts_0a_px0_bram_re', 'consts_0a_px1_bram_re', 'consts_0a_px2_bram_re', 'consts_0a_px3_bram_re'],
                       ['consts_0c_px0_bram_re', 'consts_0c_px1_bram_re', 'consts_0c_px2_bram_re', 'consts_0c_px3_bram_re'],
                       ['consts_1a_px0_bram_re', 'consts_1a_px1_bram_re', 'consts_1a_px2_bram_re', 'consts_1a_px3_bram_re'],
                       ['consts_1c_px0_bram_re', 'consts_1c_px1_bram_re', 'consts_1c_px2_bram_re', 'consts_1c_px3_bram_re']],
                      [['consts_0a_py0_bram_re', 'consts_0a_py1_bram_re', 'consts_0a_py2_bram_re', 'consts_0a_py3_bram_re'],
                       ['consts_0c_py0_bram_re', 'consts_0c_py1_bram_re', 'consts_0c_py2_bram_re', 'consts_0c_py3_bram_re'],
                       ['consts_1a_py0_bram_re', 'consts_1a_py1_bram_re', 'consts_1a_py2_bram_re', 'consts_1a_py3_bram_re'],
                       ['consts_1c_py0_bram_re', 'consts_1c_py1_bram_re', 'consts_1c_py2_bram_re', 'consts_1c_py3_bram_re']]],
                     [[['consts_0a_px0_bram_im', 'consts_0a_px1_bram_im', 'consts_0a_px2_bram_im', 'consts_0a_px3_bram_im'],
                       ['consts_0c_px0_bram_im', 'consts_0c_px1_bram_im', 'consts_0c_px2_bram_im', 'consts_0c_px3_bram_im'],
                       ['consts_1a_px0_bram_im', 'consts_1a_px1_bram_im', 'consts_1a_px2_bram_im', 'consts_1a_px3_bram_im'],
                       ['consts_1c_px0_bram_im', 'consts_1c_px1_bram_im', 'consts_1c_px2_bram_im', 'consts_1c_px3_bram_im']],
                      [['consts_0a_py0_bram_im', 'consts_0a_py1_bram_im', 'consts_0a_py2_bram_im', 'consts_0a_py3_bram_im'],
                       ['consts_0c_py0_bram_im', 'consts_0c_py1_bram_im', 'consts_0c_py2_bram_im', 'consts_0c_py3_bram_im'],
                       ['consts_1a_py0_bram_im', 'consts_1a_py1_bram_im', 'consts_1a_py2_bram_im', 'consts_1a_py3_bram_im'],
                       ['consts_1c_py0_bram_im', 'consts_1c_py1_bram_im', 'consts_1c_py2_bram_im', 'consts_1c_py3_bram_im']]]]}
                    
synth_info   = {'addr_width'  : 9,
                'word_width'  : 64,
                'data_type'   : '>u8',
                'interleave'  : True,
                'acc_len_reg' : 'syn_acc_len',
                'bram_names'  :
                [['dout0_0', 'dout0_1', 'dout0_2', 'dout0_3'], 
                 ['dout1_0', 'dout1_1', 'dout1_2', 'dout1_3']]}

# spectra settings
spec_titles = ['ZDOK0 a', 'ZDOK0 c', 'ZDOK1 a', 'ZDOK1 c']

# pocket correlator settings
chnl_start  = 1
chnl_stop   = 2048
chnl_step   = 16
corr_legends = ['a/a', 'b/a', 'c/a', 'd/a']
