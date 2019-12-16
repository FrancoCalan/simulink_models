# Basic settings
simulated  = False
roach_ip   = '192.168.1.12'
roach_port = 7147
upload     = True
program    = True
boffile    = 'adc_sync.bof.gz'
set_regs   = [{'name' : 'snap_trig' , 'val' : 0},
              {'name' : 'adc0_delay', 'val' : 0},
              {'name' : 'adc1_delay', 'val' : 0}]
reset_regs = []
bw         = 1000 # [MHz]

# Snapshot settings
snapshots    = ['adcsnap0', 'adcsnap1']
snap_samples = 256

# adc5g calibration settings
snapshots_info = [{'zdok' : 0, 'names' : ['adcsnap0']}, 
                  {'zdok' : 1, 'names' : ['adcsnap1']}]
cal_source = {'type'                : 'visa',
              'connection'          : 'TCPIP::192.168.1.34::INSTR',
              'def_freq'            : 10, # MHz
              'def_power'           : -3} # dBm
do_mmcm        = True
do_ogp         = False
do_inl         = False
load_ogp       = True
load_inl       = True
plot_snapshots = False
plot_spectra   = False
caldir         = 'calibrations'
loaddir        = '../../../Spectrometers/ROACH2/bof/calibrations_2018-12-18 19:09:38'

# Adc synchronator settings
sync_source = cal_source
