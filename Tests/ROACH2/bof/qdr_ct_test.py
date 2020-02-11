import time
import corr, qdr
import numpy as np
import matplotlib.pyplot as plt

# initialize
fpga = corr.katcp_wrapper.FpgaClient('192.168.1.12', 7147)
time.sleep(0.1)
if True:
    fpga.upload_program_bof('qdr_transpose_test/bit_files/qdr_transpose_test_135mhz.bof.gz', 3000)
    time.sleep(0.1)
    
    # calibrate qdr
    my_qdr = qdr.Qdr(fpga, 'qdr0')
    my_qdr.qdr_cal(fail_hard=True, verbosity=1)
    time.sleep(0.1)

print "FPGA clock " + str(fpga.est_brd_clk())

# read data
fpga.write_int('qdr_en', 1)
fpga.write_int('reset', 0)
fpga.write_int('reset', 1)
time.sleep(2)
orig_data = np.frombuffer(fpga.read('original' , (2**8)*(2**8)*4, 0), dtype='>u4')
tran_data = np.frombuffer(fpga.read('transpose', (2**8)*(2**8)*4, 0), dtype='>u4')

# check data correctness
rows  = 2**8
cols  = 2**8
check_data = np.arange(rows*cols)
check_data = np.reshape(check_data, (rows, cols))
check_data = np.reshape(check_data.T, (1, rows*cols))[0]
print np.array_equal(tran_data, check_data)

# plot data
plt.plot(orig_data, '-', label='original')
plt.plot(tran_data, '-', label='transpose')
plt.grid()
plt.legend()
plt.show()
