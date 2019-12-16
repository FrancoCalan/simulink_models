import json
import numpy as np
import matplotlib.pyplot as plt


datapath = "16:28"
offsets = [-15, -14, -13, -12, -11, -10, -9, -8, -7, -6, -5, 
    -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
#offsets = [-15, 15]
datafiles = [datapath + "/offset_" + str(i) + "_0.json" for i in offsets]

dataarr = []
for datafile in datafiles:
    jsondata = json.load(open(datafile))
    dataarr.append(jsondata)

plt.figure()
for data, offset in zip(dataarr, offsets):
    plt.plot(data['frequency_mhz'][1:], data['primary_signal_power_dbfs'][1:], label='offset:'+str(offset))

plt.xlabel('Frequency [MHz]')
plt.ylabel('Power [dBFS]')
#plt.legend()
plt.grid()

plt.figure()
for data, offset in zip(dataarr, offsets):
    plt.plot(data['frequency_mhz'][1:], data['filter_output_power_dbfs'][1:], label='offset:'+str(offset))

plt.xlabel('Frequency [MHz]')
plt.ylabel('Power [dBFS]')
#plt.legend()
plt.grid()

plt.figure()
for data, offset in zip(dataarr, offsets):
    plt.plot(data['frequency_mhz'][1:], data['reference_signal_power_dbfs'][1:], label='offset:'+str(offset))

plt.xlabel('Frequency [MHz]')
plt.ylabel('Power [dBFS]')
#plt.legend()
plt.grid()

plt.show()
