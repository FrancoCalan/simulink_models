# Basic settings
simulated  = False
roach_ip   = '192.168.1.12'
roach_port = 7147
upload     = True
program    = True
#boffile    = 'snap2in.bof.gz'
boffile    = 'snap4in.bof.gz'
#boffile    = 'snap16in.bof.gz'
set_regs   = []
reset_regs = []
bw         = 1000 # [MHz]

# Snapshot settings
#snapshots    = ['adcsnap0', 'adcsnap1']
snapshots    = ['adcsnap0', 'adcsnap1', 'adcsnap2', 'adcsnap3']
#snapshots    = ['snap_a1', 'snap_a2', 'snap_a3', 'snap_a4', 'snap_b1', 'snap_b2', 'snap_b3', 'snap_b4', 'snap_c1', 'snap_c2', 'snap_c3', 'snap_c4', 'snap_d1', 'snap_d2', 'snap_d3', 'snap_d4']
snap_samples = 256

# adc5g calibration settings
snapshots_info = [{'zdok' : 0, 'names' : ['adcsnap0']}, 
                  {'zdok' : 1, 'names' : ['adcsnap1']}]
cal_source = {'type'       : 'visa',
              'connection' : 'TCPIP::192.168.1.33::INSTR',
              'def_freq'   : 10, # MHz
              'def_power'  : -3} # dBm
do_mmcm        = True
do_ogp         = False
do_inl         = False
load_ogp       = True
load_inl       = True
plot_snapshots = True
plot_spectra   = True
caldir         = 'calibrations'
loaddir        = '../../../Spectrometers/ROACH2/bof/calibrations_2018-12-18 19:09:38'
