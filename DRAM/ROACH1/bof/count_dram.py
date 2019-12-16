import corr, time
import numpy as np

fpga = corr.katcp_wrapper.FpgaClient('192.168.1.11')
time.sleep(1)

fpga.progdev('count_dram.bof')

# Activate counter so you start to write in dram
print("Writing counter data in DRAM...")
fpga.write_int('reset', 0)
fpga.write_int('enable', 1)
time.sleep(1)
print("done")

# check if written values are the expected
print("Reading data from DRAM...")
tstart = time.time()
ii = 24
oo = 4
for i in range(2**oo):
    print 16*2**(ii-oo)
    data_arr = np.frombuffer(fpga.read_dram(16*2**(ii-oo), 16*2**(ii-oo)*i), dtype='>u8')
    expected_arr = 10*np.array(range(2**(ii-oo)*i, 2**(ii-oo)*(i+1)), dtype='>u8')
    expected_arr = np.reshape(np.vstack((expected_arr, expected_arr+1)), 
        (1, 2*len(expected_arr)), order='F')[0]
    #print "Read array:" + str(data_arr)
    if not np.array_equal(data_arr, expected_arr):
        print("Read and expected array doesn't match:")
        print("Read array:" + str(data_arr))
        print("Expected array:" + str(expected_arr))
print("Read time: " + str(time.time() - tstart) + "[s]")
print("done")
