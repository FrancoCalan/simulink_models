import json
import matplotlib.pyplot as plt

with open("frequency_response spec2in_4096ch_1080mhz.bof 2019-09-06 12:08:04.json") as json_file:
    data = json.load(json_file)

plt.plot(data['freqs'], data['frequency_response'][1])
plt.show()
