# -*- coding: utf-8 -*-
# v2.2 para 10 detectores en paralelo

import corr
import numpy as np
import time
import matplotlib.pyplot as plt
import matplotlib.animation as animation

"""
Detector ACC v2.2 - ROACH 2

Obtiene la señal de acumulación de 10 detectores en paralelo y las grafica en tiempo real
Pueden seleccionarse los DMs de cada señal y mostrará los tiempos y retardos respectivos,
así como la frecuencia que debe colocar en el AWG

"""

global line

# Parámetros FRB
k       = 4.15E6            # K_DM (MHz^2pc^-1cm^3ms)
BW      = 540               # Ancho de Banda (MHz)
f_cen   = 1100              # Frecuencia central (MHz)
f_low   = f_cen-BW/2        # Límite inferior de detección (MHz)
f_high  = f_cen+BW/2        # Límite superior de detección (MHz)

# Parámetros del modelo
f_fpga      = 67.5E6*2          # Frecuencia de reloj
fft_chans   = 64                # Canales de la FFT
par_chans   = 8                 # Número de streams en paralelo de la FFT
factor      = 62/64.0  		    # Relative number of channels to the total spectrum of simulated FRB 

parameters  = [f_low,f_high,k,fft_chans,factor,f_fpga,par_chans]

# FRB_param: Función para obtener los parámetros de tiempo y acumulaciones de un FRB dado un DM
def FRB_param(number,DM,param):
    t_dd    = DM*((param[0]**-2-param[1]**-2)*param[2])*1E-3     # Duración del pulso dispersado (factor 1E3 pues k está en ms)
    f_awg   = 1/(t_dd)                                           # Frecuencia del AWG
    t_d     = t_dd/(param[3]*param[4])                           # Duración del pulso dedispersado
    n_acc   = t_d*param[5]*param[6]*param[4]/param[3]            # Número de acumulaciones
    print('*** FRB'+str(number)+' ***')
    print('DM: '+str(DM)+' (pc*cm^-3)')
    print('Tiempo de barrido: '+str(int(t_dd*1E3))+' (ms)')
    print('Número de acumulaciones: '+str(round(n_acc,2)))
    print('Frecuencia AWG: '+str(round(f_awg,7))+' (Hz)')
    return t_dd,f_awg,t_d,n_acc

# FRB 1
DM1 = 200
t_dd1,f_awg1,t_d1,number_acc1 = FRB_param(1,DM1,parameters)
# FRB 2
DM2 = 250
t_dd2,f_awg2,t_d2,number_acc2 = FRB_param(2,DM2,parameters)
# FRB 3
DM3 = 300
t_dd3,f_awg3,t_d3,number_acc3 = FRB_param(3,DM3,parameters)
# FRB 4
DM4 = 350
t_dd4,f_awg4,t_d4,number_acc4 = FRB_param(4,DM4,parameters)
# FRB 5
DM5 = 400
t_dd5,f_awg5,t_d5,number_acc5 = FRB_param(5,DM5,parameters)
# FRB 6
DM6 = 450
t_dd6,f_awg6,t_d6,number_acc6 = FRB_param(6,DM6,parameters)
# FRB 7
DM7 = 500
t_dd7,f_awg7,t_d7,number_acc7 = FRB_param(7,DM7,parameters)
# FRB 8
DM8 = 550
t_dd8,f_awg8,t_d8,number_acc8 = FRB_param(8,DM8,parameters)
# FRB 9
DM9 = 600
t_dd9,f_awg9,t_d9,number_acc9 = FRB_param(9,DM9,parameters)
# FRB 10
DM10 = 650
t_dd10,f_awg10,t_d10,number_acc10 = FRB_param(10,DM10,parameters)

#Create fpga object (sleep for stability)
fpga = corr.katcp_wrapper.FpgaClient('192.168.1.12')

# Upload bof file to fpga
# fpga.upload_program_bof('detector_roach2_v2.2.bof',60000)
# print('fpga programada, puede comentar esta sección')
time.sleep(2)

# read_ram: Reads a single ram block of user-defined bytesize 
def read_ram(ram_name, bytesize):
	raw_data = fpga.read(ram_name,bytesize)
	ram_data = np.fromstring(raw_data,dtype='>u8')
	return ram_data

# acc_lim: Get some samples from ACC# register to get detection limit
def acc_lim(acc_name):
    samp = 30   # Number of samples
    acc_array = [1]*samp
    for i in range(samp):
        acc = read_ram(acc_name,2**9*8)
        acc_array[i] = acc
    acc_avg = np.mean(acc_array)
    acc_std = np.std(acc_array)
    acc_limit = acc_avg + 8*acc_std

    print('FRB '+acc_name[3:]+':')
    print('Avg ACC (dB): '+str(10*np.log10(acc_avg)))
    print('Std ACC (dB): '+str(10*np.log10(acc_std)))
    print('ACC Lim (dB): '+str(10*np.log10(acc_limit)))
    return acc_limit,acc_std
 
# init: init function for animation 
def init():
    line[0].set_data([],[])
    line[1].set_data([],[])
    line[2].set_data([],[])
    line[3].set_data([],[])
    line[4].set_data([],[])
    line[5].set_data([],[])
    line[6].set_data([],[])
    line[7].set_data([],[])
    line[8].set_data([],[])
    line[9].set_data([],[])
    line[10].set_data([],[])
    line[11].set_data([],[])
    line[12].set_data([],[])
    line[13].set_data([],[])
    line[14].set_data([],[])
    line[15].set_data([],[])
    line[16].set_data([],[])
    line[17].set_data([],[])
    line[18].set_data([],[])
    line[19].set_data([],[])
    return line

# Write registers
fpga.write_int('acc_len1',number_acc1)
fpga.write_int('acc_len2',number_acc2)
fpga.write_int('acc_len3',number_acc3)
fpga.write_int('acc_len4',number_acc4)
fpga.write_int('acc_len5',number_acc5)
fpga.write_int('acc_len6',number_acc6)
fpga.write_int('acc_len7',number_acc7)
fpga.write_int('acc_len8',number_acc8)
fpga.write_int('acc_len9',number_acc9)
fpga.write_int('acc_len10',number_acc10)
# fpga.write_int('cnt_rst',1)
# fpga.write_int('cnt_rst',0)
time.sleep(2)	

# Create figure
fig = plt.figure()
ax1 = fig.add_subplot(5,2,1)
ax2 = fig.add_subplot(5,2,2)
ax3 = fig.add_subplot(5,2,3)
ax4 = fig.add_subplot(5,2,4)
ax5 = fig.add_subplot(5,2,5)
ax6 = fig.add_subplot(5,2,6)
ax7 = fig.add_subplot(5,2,7)
ax8 = fig.add_subplot(5,2,8)
ax9 = fig.add_subplot(5,2,9)
ax10 = fig.add_subplot(5,2,10)

# Calculate detection limits for DMs
acc_lim1,std1 = acc_lim('ACC1')
acc_lim2,std2 = acc_lim('ACC2')
acc_lim3,std3 = acc_lim('ACC3')
acc_lim4,std4 = acc_lim('ACC4')
acc_lim5,std5 = acc_lim('ACC5')
acc_lim6,std6 = acc_lim('ACC6')
acc_lim7,std7 = acc_lim('ACC7')
acc_lim8,std8 = acc_lim('ACC8')
acc_lim9,std9 = acc_lim('ACC9')
acc_lim10,std10 = acc_lim('ACC10')
# Detection limits to dB
acc_lim1_db = 10*np.log10(acc_lim1)
acc_lim2_db = 10*np.log10(acc_lim2)
acc_lim3_db = 10*np.log10(acc_lim3)
acc_lim4_db = 10*np.log10(acc_lim4)
acc_lim5_db = 10*np.log10(acc_lim5)
acc_lim6_db = 10*np.log10(acc_lim6)
acc_lim7_db = 10*np.log10(acc_lim7)
acc_lim8_db = 10*np.log10(acc_lim8)
acc_lim9_db = 10*np.log10(acc_lim9)
acc_lim10_db = 10*np.log10(acc_lim10)

# x-Axis limit
ax1.set_xlim(-5,517)
ax2.set_xlim(-5,517)
ax3.set_xlim(-5,517)
ax4.set_xlim(-5,517)
ax5.set_xlim(-5,517)
ax6.set_xlim(-5,517)
ax7.set_xlim(-5,517)
ax8.set_xlim(-5,517)
ax9.set_xlim(-5,517)
ax10.set_xlim(-5,517)

# Set how many deviations from acc_lim will plot data
low = 15
high = 5

# y-Axis limit
ax1.set_ylim(10*np.log10(acc_lim1-low*std1),10*np.log10(acc_lim1+high*std1))
ax2.set_ylim(10*np.log10(acc_lim2-low*std2),10*np.log10(acc_lim2+high*std2))
ax3.set_ylim(10*np.log10(acc_lim3-low*std3),10*np.log10(acc_lim3+high*std3))
ax4.set_ylim(10*np.log10(acc_lim4-low*std4),10*np.log10(acc_lim4+high*std4))
ax5.set_ylim(10*np.log10(acc_lim5-low*std5),10*np.log10(acc_lim5+high*std5))
ax6.set_ylim(10*np.log10(acc_lim6-low*std6),10*np.log10(acc_lim6+high*std6))
ax7.set_ylim(10*np.log10(acc_lim7-low*std7),10*np.log10(acc_lim7+high*std7))
ax8.set_ylim(10*np.log10(acc_lim8-low*std8),10*np.log10(acc_lim8+high*std8))
ax9.set_ylim(10*np.log10(acc_lim9-low*std9),10*np.log10(acc_lim9+high*std9))
ax10.set_ylim(10*np.log10(acc_lim10-low*std10),10*np.log10(acc_lim10+high*std10))

# Create arrays. Will contain data to be plotted
line1, = ax1.plot([],[],lw=2, marker = '.', linestyle='-')  # ACC1
line2, = ax2.plot([],[],lw=2, marker = '.', linestyle='-')  # ACC2
line3, = ax3.plot([],[],lw=2, marker = '.', linestyle='-')  # ACC3
line4, = ax4.plot([],[],lw=2, marker = '.', linestyle='-')  # ACC4
line5, = ax5.plot([],[],lw=2, marker = '.', linestyle='-')  # ACC5
line6, = ax6.plot([],[],lw=2, marker = '.', linestyle='-')  # ACC6
line7, = ax7.plot([],[],lw=2, marker = '.', linestyle='-')  # ACC7
line8, = ax8.plot([],[],lw=2, marker = '.', linestyle='-')  # ACC8
line9, = ax9.plot([],[],lw=2, marker = '.', linestyle='-')  # ACC9
line10,= ax10.plot([],[],lw=2, marker = '.', linestyle='-')  # ACC10
line11, = ax1.plot([],[],lw=2, marker = None, linestyle='-',label= "Umbral: "+str(round(10*np.log10(acc_lim1),2))+" dB" )
line12, = ax2.plot([],[],lw=2, marker = None, linestyle='-',label= "Umbral: "+str(round(10*np.log10(acc_lim2),2))+" dB" )
line13, = ax3.plot([],[],lw=2, marker = None, linestyle='-',label= "Umbral: "+str(round(10*np.log10(acc_lim3),2))+" dB" )
line14, = ax4.plot([],[],lw=2, marker = None, linestyle='-',label= "Umbral: "+str(round(10*np.log10(acc_lim4),2))+" dB" )
line15, = ax5.plot([],[],lw=2, marker = None, linestyle='-',label= "Umbral: "+str(round(10*np.log10(acc_lim5),2))+" dB" )
line16, = ax6.plot([],[],lw=2, marker = None, linestyle='-',label= "Umbral: "+str(round(10*np.log10(acc_lim6),2))+" dB" )
line17, = ax7.plot([],[],lw=2, marker = None, linestyle='-',label= "Umbral: "+str(round(10*np.log10(acc_lim7),2))+" dB" )
line18, = ax8.plot([],[],lw=2, marker = None, linestyle='-',label= "Umbral: "+str(round(10*np.log10(acc_lim8),2))+" dB" )
line19, = ax9.plot([],[],lw=2, marker = None, linestyle='-',label= "Umbral: "+str(round(10*np.log10(acc_lim9),2))+" dB" )
line20, = ax10.plot([],[],lw=2, marker = None, linestyle='-',label= "Umbral: "+str(round(10*np.log10(acc_lim10),2))+" dB" )

line = [line1,line2,line3,line4,line5,line6,line7,line8,line9,line10,
line11,line12,line13,line14,line15,line16,line17,line18,line19,line20]

# Create x-axis array
acc_x = np.linspace(0,511,512,endpoint=True)

# Set detection limit
fpga.write_int('theta1',2^32-1)
fpga.write_int('theta2',2^32-1)
fpga.write_int('theta3',2^32-1)
fpga.write_int('theta4',2^32-1)
fpga.write_int('theta5',2^32-1)
fpga.write_int('theta6',2^32-1)
fpga.write_int('theta7',2^32-1)
fpga.write_int('theta8',2^32-1)
fpga.write_int('theta9',2^32-1)
fpga.write_int('theta10',2^32-1)
time.sleep(2)

# Animation function
def animate(i):
    # Obtain data from registers
    acc1 = np.array(read_ram('ACC1',2**9*8))
    acc2 = np.array(read_ram('ACC2',2**9*8))
    acc3 = np.array(read_ram('ACC3',2**9*8))
    acc4 = np.array(read_ram('ACC4',2**9*8))
    acc5 = np.array(read_ram('ACC5',2**9*8))
    acc6 = np.array(read_ram('ACC6',2**9*8))
    acc7 = np.array(read_ram('ACC7',2**9*8))
    acc8 = np.array(read_ram('ACC8',2**9*8))
    acc9 = np.array(read_ram('ACC9',2**9*8))
    acc10 = np.array(read_ram('ACC10',2**9*8))
    # Data in dB
    acc_db1 = 10*np.log10(acc1)
    acc_db2 = 10*np.log10(acc2)
    acc_db3 = 10*np.log10(acc3)
    acc_db4 = 10*np.log10(acc4)
    acc_db5 = 10*np.log10(acc5)
    acc_db6 = 10*np.log10(acc6)
    acc_db7 = 10*np.log10(acc7)
    acc_db8 = 10*np.log10(acc8)
    acc_db9 = 10*np.log10(acc9)
    acc_db10 = 10*np.log10(acc10)
    #Asign data to arrays
    line[0].set_data(acc_x,acc_db1)
    line[1].set_data(acc_x,acc_db2)
    line[2].set_data(acc_x,acc_db3)
    line[3].set_data(acc_x,acc_db4)
    line[4].set_data(acc_x,acc_db5)
    line[5].set_data(acc_x,acc_db6)
    line[6].set_data(acc_x,acc_db7)
    line[7].set_data(acc_x,acc_db8)
    line[8].set_data(acc_x,acc_db9)
    line[9].set_data(acc_x,acc_db10)
    line[10].set_data(acc_x,len(acc_x)*[acc_lim1_db])
    line[11].set_data(acc_x,len(acc_x)*[acc_lim2_db])
    line[12].set_data(acc_x,len(acc_x)*[acc_lim3_db])
    line[13].set_data(acc_x,len(acc_x)*[acc_lim4_db])
    line[14].set_data(acc_x,len(acc_x)*[acc_lim5_db])
    line[15].set_data(acc_x,len(acc_x)*[acc_lim6_db])
    line[16].set_data(acc_x,len(acc_x)*[acc_lim7_db])
    line[17].set_data(acc_x,len(acc_x)*[acc_lim8_db])
    line[18].set_data(acc_x,len(acc_x)*[acc_lim9_db])
    line[19].set_data(acc_x,len(acc_x)*[acc_lim10_db])
    return line

anim = animation.FuncAnimation(fig,animate,blit=True,interval=10,init_func=init,repeat=True)

fig.canvas.set_window_title('Parallel Detector v2.0')

fig.suptitle('Espectros para deteccion de FRB')

ax1.title.set_text('DM '+str(DM1))
ax1.set_ylabel('Potencia (dB)')
ax1.grid()
ax1.legend()

ax2.title.set_text('DM '+str(DM2))
ax2.set_ylabel('Potencia (dB)')
ax2.grid()
ax2.legend()

ax3.title.set_text('DM '+str(DM3))
ax3.set_ylabel('Potencia (dB)')
ax3.grid()
ax3.legend()

ax4.title.set_text('DM '+str(DM4))
ax4.set_ylabel('Potencia (dB)')
ax4.grid()
ax4.legend()

ax5.title.set_text('DM '+str(DM5))
ax5.set_ylabel('Potencia (dB)')
ax5.grid()
ax5.legend()

ax6.title.set_text('DM '+str(DM6))
ax6.set_ylabel('Potencia (dB)')
ax6.grid()
ax6.legend()

ax7.title.set_text('DM '+str(DM7))
ax7.set_ylabel('Potencia (dB)')
ax7.grid()
ax7.legend()

ax8.title.set_text('DM '+str(DM8))
ax8.set_ylabel('Potencia (dB)')
ax8.grid()
ax8.legend()

ax9.title.set_text('DM '+str(DM9))
ax9.set_ylabel('Potencia (dB)')
ax9.grid()
ax9.legend()

ax10.title.set_text('DM '+str(DM10))
ax10.set_ylabel('Potencia (dB)')
ax10.grid()
ax10.legend()

plt.show()
