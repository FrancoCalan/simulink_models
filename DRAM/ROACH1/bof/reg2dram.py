import corr, time
import numpy as np

fpga = corr.katcp_wrapper.FpgaClient('192.168.1.11')
time.sleep(1)

fpga.progdev('reg2dram.bof')

# write some value to DRAM
fpga.write_int('valid', 1)
#loop_arr = range(2**4)
#loop_arr = range(2**10, 2**10+2**4, 1)
loop_arr = range(2**20, 2**20+2**4, 1)
print("Writing data into DRAM...")
for i in loop_arr:
    fpga.write_int('address', i)
    fpga.write_int('reg0', 10*i)
    fpga.write_int('reg1', 20*i)
    fpga.write_int('reg2', 30*i)
    fpga.write_int('reg3', 40*i)
print("done")

# check if written value is the expected
print("Reading data from DRAM...")
for i in loop_arr:
    data_arr = np.frombuffer(fpga.read_dram(32, 32*i), dtype='>u4')
    expected_arr = np.array([10*i, 20*i, 30*i, 40*i, 
                             10*i, 20*i, 30*i, 40*i])
    if np.array_equal(data_arr, expected_arr):
        print "Read and expected array are equal!: " + str(expected_arr.tolist())
    else:
        print "Read array from dram and expected array are not equal"
        print "Read array:" + str(data_arr)
        print "Expected array:" + str(expected_arr)
print("done")
