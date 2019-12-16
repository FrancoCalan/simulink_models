# Basic settings
simulated  = False
roach_ip   = '192.168.1.11'
roach_port = 7147
upload     = False
program    = True
boffile    = 'modificar_acc_compilar_2019_Mar_07_1912.bof'
set_regs   = [{'name' : 'acc_len', 'val' : 18750},
              {'name' : 'theta',   'val' : 2**10}]
reset_regs = ['cnt_rst']
bw          = 60 # [MHz]

# Snapshot settings
snapshots    = ['adcsnap0']
snap_samples = 256

# Spectrometer Settings
plot_titles = ['disp', 'dedsip', 'dedisp freeze']
spec_info   = {'addr_width'  : 6,
               'word_width'  : 64,
               'data_type'   : '>u8',
               'acc_len_reg' : 'acc_len',
               'bram_names'  : ['Spec', 'Spec1', 'Spec2']}
