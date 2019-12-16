import json
import numpy as np
import matplotlib.pyplot as plt

datapath = "19:04"
offsets = [-15, -14, -13, -12, -11, -10, -9, -8, -7, -6, -5, 
    -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
datafiles = [datapath + "/offset_" + str(i) + "_0.json" for i in offsets]

dataarr = []
for datafile in datafiles:
    jsondata = json.load(open(datafile))
    dataarr.append(jsondata)

prim_power = []
filt_power = []
ref__power = []

#minind = 1800; maxind = minind+100
minind = 100; maxind = 2000
#minind = 100; maxind = 1300
#minind = 1; maxind = 2048

for data in dataarr:
    prim_powers = 10**(np.array(data['primary_signal_power_dbfs'])/10)
    filt_powers = 10**(np.array(data['filter_output_power_dbfs'])/10)
    ref__powers = 10**(np.array(data['reference_signal_power_dbfs'])/10)
    prim_power.append(10*np.log10(np.sum(prim_powers[minind:maxind])))
    filt_power.append(10*np.log10(np.sum(filt_powers[minind:maxind])))
    ref__power.append(10*np.log10(np.sum(ref__powers[minind:maxind])))

plt.figure()
plt.plot(offsets, prim_power, 'x-r', label='Primary signal power')
plt.plot(offsets, filt_power, 'x-b', label='Filter output power')
plt.xlabel('Offset [deg]')
plt.ylabel('Total Power [dB]')
plt.legend()
plt.grid()
plt.figure()
plt.plot(offsets, ref__power, 'x-g', label='Reference signal power')
plt.xlabel('Offset [deg]')
plt.ylabel('Total Power [dB]')
plt.legend()
plt.grid()
plt.show()
