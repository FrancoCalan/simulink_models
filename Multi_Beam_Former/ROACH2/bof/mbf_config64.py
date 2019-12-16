# Basic settings
simulated  = False
roach_ip   = '192.168.1.13'
roach_port = 7147
upload     = False
program    = False
boffile    = 'mbf_64beams_freerun.bof.gz'
set_regs   = [{'name' : 'pow_acc_len', 'val' : 2**10},
              {'name' : 'cal_acc_len', 'val' : 2**10},
              {'name' : 'bf_acc_len',  'val' : 2**10}]
reset_regs = ['cal_cnt_rst', 'bf_cnt_rst']
bw         = 140.0 # [MHz]

# Snapshot settings
snapshots    = ['snap_adc_a1', 'snap_adc_a2', 'snap_adc_a3', 'snap_adc_a4', 
                'snap_adc_b1', 'snap_adc_b2', 'snap_adc_b3', 'snap_adc_b4', 
                'snap_adc_c1', 'snap_adc_c2', 'snap_adc_c3', 'snap_adc_c4', 
                'snap_adc_d1', 'snap_adc_d2', 'snap_adc_d3', 'snap_adc_d4']
snap_samples = 64

# Full power settings
pow_info = {'acc_len_reg' : 'pow_acc_len',
            'reg_list'    : ['power_adc_a1', 'power_adc_a2', 'power_adc_a3', 'power_adc_a4', 
                             'power_adc_b1', 'power_adc_b2', 'power_adc_b3', 'power_adc_b4', 
                             'power_adc_c1', 'power_adc_c2', 'power_adc_c3', 'power_adc_c4', 
                             'power_adc_d1', 'power_adc_d2', 'power_adc_d3', 'power_adc_d4']}

# spectra info
spec_titles = ['a1', 'a2', 'a3', 'a4', 'b1', 'b2', 'b3', 'b4', 'c1', 'c2', 'c3', 'c4', 'd1', 'd2', 'd3', 'd4']
cal_phase_info = {'const_nbits'  : 32,
                  'const_bin_pt' : 17,
                  'phasor_regs'  : ['cal_phase_re', 'cal_phase_im'],
                  'addr_regs'    : 'cal_phase_addr',
                  'we_reg'       : 'cal_phase_we'}
                  
spec_info = { 'addr_width'      : 8,
              'word_width'      : 128,
              'data_type'       : '>u8',
              'deinterleave_by' : 2,
              'acc_len_reg'     : 'cal_acc_len',
              'req_reg'         : 'cal_new_acc',
              'read_count_reg'  : 'acc_control_acc_count',
              'bram_names'      : ['cal_probe0_xpow_pow0', 'cal_probe0_xpow_pow1',
                                   'cal_probe1_xpow_pow0', 'cal_probe1_xpow_pow1',
                                   'cal_probe2_xpow_pow0', 'cal_probe2_xpow_pow1',
                                   'cal_probe3_xpow_pow0', 'cal_probe3_xpow_pow1']}

# mbf_calibrator settings
freq_chnl = 20 # = 10.9375MHz for BW=140MHz
#freq_chnl = 2 # = 1.09375MHz for BW=140MHz
#freq_chnl = 200 
cal_crosspow_info = { 'addr_width'      : 8,
                      'word_width'      : 128,
                      'data_type'       : '>i8',
                      'acc_len_reg'     : 'cal_acc_len',
                      'req_reg'         : 'cal_new_acc',
                      'read_count_reg'  : 'acc_control_acc_count',
                      'bram_names'      : ['cal_probe0_xab_ab0', 'cal_probe0_xab_ab1', 'cal_probe0_xab_ab2', 'cal_probe0_xab_ab3',
                                           'cal_probe1_xab_ab0', 'cal_probe1_xab_ab1', 'cal_probe1_xab_ab2', 'cal_probe1_xab_ab3',
                                           'cal_probe2_xab_ab0', 'cal_probe2_xab_ab1', 'cal_probe2_xab_ab2', 'cal_probe2_xab_ab3',
                                           'cal_probe3_xab_ab0', 'cal_probe3_xab_ab1', 'cal_probe3_xab_ab2', 'cal_probe3_xab_ab3']}

# mbf single beamscan settings
ideal_phase_consts = False
array_info = {'freq'  : 10.9375e6, # observation frequency (down-converted)
              'speed'  : 3e8,      # speed of light
              'el_sep' : 0.5,      # elements separation in wavelength units
              'el_pos' : [[( 1.5, 0,  1.5), ( 0.5, 0,  1.5), (-0.5, 0,  1.5), (-1.5, 0,  1.5)],
                          [( 1.5, 0,  0.5), ( 0.5, 0,  0.5), (-0.5, 0,  0.5), (-1.5, 0,  0.5)],
                          [( 1.5, 0, -0.5), ( 0.5, 0, -0.5), (-0.5, 0, -0.5), (-1.5, 0, -0.5)],
                          [( 1.5, 0, -1.5), ( 0.5, 0, -1.5), (-0.5, 0, -1.5), (-1.5, 0, -1.5)]]} # elements positions in arbitrary units

#az_ang_range =  [-35, 35, 10]; el_ang_range =  [-35, 35, 10]
#az_ang_range =  [-42, 42, 12]; el_ang_range =  [-42, 42, 12]
#az_ang_range =  [-49, 49, 14]; el_ang_range =  [-49, 49, 14]
az_ang_range =  [-56, 56, 16]; el_ang_range =  [-56, 56, 16]
#az_ang_range =  [-63, 63, 18]; el_ang_range =  [-63, 63, 18]
#az_ang_range =  [-70, 70, 20]; el_ang_range =  [-70, 70, 20]
interpolation = 'none'
#interpolation = 'spline36'

bf_phase_info = {'const_nbits'  : 32,
                 'const_bin_pt' : 17,
                 'phasor_regs'  : ['bf_phase_re', 'bf_phase_im'],
                 'addr_regs'    : ['bf_addr_y', 'bf_addr_x', 'bf_addr_t', 'bf_addr_sub'],
                 'we_reg'       : 'bf_phase_we'}

bf_spec_info = {'addr_width'      : 10,
                'word_width'      : 64,
                'data_type'       : '>u8',
                'divide_by'       : 4,
                'acc_len_reg'     : 'bf_acc_len',
                'bram_names'      : ['bf_probe0_xpow_s0',  'bf_probe0_xpow_s1',  'bf_probe0_xpow_s2',  'bf_probe0_xpow_s3',
                                     'bf_probe0_xpow_s4',  'bf_probe0_xpow_s5',  'bf_probe0_xpow_s6',  'bf_probe0_xpow_s7',
                                     'bf_probe0_xpow_s8',  'bf_probe0_xpow_s9',  'bf_probe0_xpow_s10', 'bf_probe0_xpow_s11',
                                     'bf_probe0_xpow_s12', 'bf_probe0_xpow_s13', 'bf_probe0_xpow_s14', 'bf_probe0_xpow_s15']}

# multibeam animator settings
steer_beams = False
plot_db     = False
