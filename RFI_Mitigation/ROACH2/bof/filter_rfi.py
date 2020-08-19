# Script to filter RFI with the kesteven filter model. Plots
# the spectrum of the primary signal, reference signal and
# the filter output. Also add some user interface to control 
# the filter and show additional plots.
import time
import numexpr
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import Tkinter as Tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import calandigital as cd
from kestfilt_parameters import *

def main():
    # initialization
    roach = cd.initialize_roach(roach_ip)

    print("Setting model registers...")
    roach.write_int(acc_len_reg, acc_len)
    roach.write_int(filter_gain_reg, filter_gain)
    roach.write_int(filter_acc_reg, filter_acc)
    roach.write_int(filter_chnl_reg, filter_chnl)
    print("done")
    print("Resseting counter registers...")
    roach.write_int(cnt_rst_reg, 1)
    roach.write_int(cnt_rst_reg, 0)
    print("done")

    print("Setting GUI elements...")
    fig, lines = create_window(roach)
    print("done.")

    # animation function
    def animate(_):
        for line, specbrams in zip(lines, specbrams_list):
            # get spectral data
            specdata = cd.read_interleave_data(roach, 
                specbrams, spec_addr_width, spec_word_width, 
                spec_data_type)
            specdata = cd.scale_and_dBFS_specdata(specdata,
                acc_len, dBFS)
            line.set_data(freqs, specdata)
        return lines

    anim = animation.FuncAnimation(fig, animate, blit=True)
    Tk.mainloop()

def create_window(roach):
    """
    Create wondow for the RFI Filter
    """
    # create window
    root = Tk.Tk()

    # add matplotlib figure and toolbar
    fig, lines = create_figure(root)

    # create button frame and buttons
    button_frame = Tk.Frame(master=root)
    button_frame.pack(side=Tk.TOP, anchor="w")
    add_save_button(roach, button_frame)
    add_reset_button(roach, button_frame)
    add_filter_button(roach, button_frame)
    # plot convergence button
    conv_button = Tk.Button(button_frame, 
        text='Plot convergence', 
        command=lambda: plot_convergence(roach))
    conv_button.pack(side=Tk.LEFT)
    # plot stability button
    stab_button = Tk.Button(button_frame, 
        text='Plot stability', 
        command=lambda: plot_stability(roach))
    stab_button.pack(side=Tk.LEFT)

    # add regiter entries
    add_reg_entry(roach, root, acc_len_reg)
    add_reg_entry(roach, root, filter_gain_reg)
    add_reg_entry(roach, root, filter_acc_reg)
    add_reg_entry(roach, root, filter_chnl_reg)

    return fig, lines

def create_figure(root):
    """
    Create the figure that contains the plots of the filter.
    """
    fig = plt.Figure()
    fig.set_tight_layout(True)
    canvas = FigureCanvasTkAgg(fig, master=root)
    toolbar = NavigationToolbar2Tk(canvas, root)
    toolbar.update()
    canvas._tkcanvas.pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)        

    # add axes to figure
    ax1 = fig.add_subplot(2,2,1)
    ax2 = fig.add_subplot(2,2,2)
    ax3 = fig.add_subplot(2,2,3)
    axes = [ax1, ax2, ax3]
    titles = ["Primary Signal", "Reference Signal", "Filter Output"]

    # define axes and create plot lines
    lines = []
    for ax, title in zip(axes, titles):
        ax.set_xlim(0, bandwidth)
        ax.set_ylim(-dBFS-2, 0)
        ax.set_xlabel('Frequency [MHz]')
        ax.set_ylabel('Power [dBFS]')
        ax.set_title(title)
        ax.grid()

        line, = ax.plot([], [], animated=True)
        lines.append(line)

    return fig, lines

def add_save_button(roach, button_frame):
    """
    Add save button to the button panel of the GUI.
    Save the plotted data into a file.
    """
    save_button = Tk.Button(button_frame, text="Save data")
    def save():
        specdata_list = []
        for specbrams in specbrams_list:
            specdata = cd.read_interleave_data(roach, 
                specbrams, spec_addr_width, spec_word_width, 
                spec_data_type)
            specdata_list.append(specdata)
        np.savez("filter_data", prim=specdata_list[0],
            ref=specdata_list[1],
            output=specdata_list[2])
        print("Data saved")
    save_button.config(command=save)
    save_button.pack(side=Tk.LEFT)

def add_reset_button(roach, button_frame):
    """
    Add reset button to the button panel of the GUI.
    It reset the cnt_rst register of the model.
    """
    reset_button = Tk.Button(button_frame, text="Reset")
    def reset():
        roach.write_int(cnt_rst_reg, 1)
        roach.write_int(cnt_rst_reg, 0)
        print("ROACH reset")
    reset_button.config(command=reset)
    reset_button.pack(side=Tk.LEFT)

def add_filter_button(roach, button_frame):
    """
    Add filter button to the button panel of the GUI.
    It toggles the state of the rfi filter, on and off.
    """
    filter_button = Tk.Button(button_frame, text="Filter off")
    def toggle_filter():
        if roach.read_int(filter_on_reg) == 1:
            filter_button.config(relief=Tk.RAISED)
            filter_button.config(text="Filter off")
            roach.write_int(filter_on_reg, 0)
            print("Filter off")
        else:
            filter_button.config(relief=Tk.SUNKEN)
            filter_button.config(text="Filter on")
            roach.write_int(filter_on_reg, 1)
            print("Filter on")
    filter_button.config(command=toggle_filter)
    filter_button.pack(side=Tk.LEFT)

def add_reg_entry(roach, root, reg):
    """
    Add a text entry to the GUI to modify a register in FPGA.
    The desired value must be written in the entry textbox,
    and the value is assigned by pressing <Return> with the
    textbox focused.
    """
    # add frame
    frame = Tk.Frame(master=root)
    frame.pack(side = Tk.TOP, anchor="w")
    # add label
    label = Tk.Label(frame, text=reg+":")
    label.pack(side=Tk.LEFT)
    # add entry
    entry = Tk.Entry(frame)
    entry.insert(Tk.END, roach.read_int(reg))
    entry.pack(side=Tk.LEFT)
    def set_reg_from_entry():
        string_val = entry.get()
        try:
            val = int(numexpr.evaluate(string_val))
        except:
            raise Exception('Unable to parse value in textbox: ' 
                + string_val)
        print("Set value " + str(val) + " to reg " + reg)
        roach.write_int(reg, val)
    entry.bind('<Return>', lambda x: set_reg_from_entry())

def plot_convergence(roach):
    # useful data
    nspecs = 2**conv_addr_width
    time = np.arange(0, nspecs) * (1.0/bandwidth) * nchannels

    # create window
    root = Tk.Tk()

    # create figure
    fig = plt.Figure()
    fig.set_tight_layout(True)
    canvas = FigureCanvasTkAgg(fig, master=root)
    toolbar = NavigationToolbar2Tk(canvas, root)
    toolbar.update()
    canvas._tkcanvas.pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)        

    # create axis
    ax = fig.add_subplot(1,1,1)
    ax.set_ylim((-100, 10))
    ax.set_xlabel('Time [$\mu$s]')
    ax.set_ylabel('Power [dBFS]')
    ax.grid()

    # add save button
    button_frame = Tk.Frame(master=root)
    button_frame.pack(side=Tk.TOP, anchor="w")
    add_conv_save_button(roach, button_frame)

    # get data
    chnl, max, mean = get_conv_data(roach)
    chnl = cd.scale_and_dBFS_specdata(chnl, 1, dBFS)
    max  = cd.scale_and_dBFS_specdata(max,  1, dBFS)
    mean = cd.scale_and_dBFS_specdata(chnl, nspecs, dBFS)

    ax.plot(time, chnl, label="channel")
    ax.plot(time, max, label="max")
    ax.plot(time, mean, label="mean")

def add_conv_save_button(roach, button_frame):
    """
    Save the convergence data into a file.
    """
    save_button = Tk.Button(button_frame, text="Save data")
    def save():
        chnl, max, mean = get_conv_data(roach)
        np.savez("convergence_data", chnl=chnl, max=max, 
            mean=mean)
        print("Data saved")
    save_button.config(command=save)
    save_button.pack(side=Tk.LEFT)

def get_conv_data(roach):
    chnl_real = cd.read_data(roach, bram_chnl2[0], 
        chnl_addr_width, chnl_word_width, chnl_data_type)
    chnl_imag = cd.read_data(roach, bram_chnl2[1], 
        chnl_addr_width, chnl_word_width, chnl_data_type)
    chnl = chnl_real**2 + chnl_imag**2
    max  = cd.read_data(roach, bram_max,  conv_addr_width,
        conv_word_width, conv_data_type)
    mean = cd.read_data(roach, bram_mean, conv_addr_width,
        conv_word_width, conv_data_type)
    return chnl, max, mean

def plot_stability(roach):
    # useful data
    nspecs = 2**chnl_addr_width
    time = np.arange(0, nspecs) * (1.0/bandwidth) * nchannels

    # create window
    root = Tk.Tk()

    # create figure
    fig = plt.Figure()
    fig.set_tight_layout(True)
    canvas = FigureCanvasTkAgg(fig, master=root)
    toolbar = NavigationToolbar2Tk(canvas, root)
    toolbar.update()
    canvas._tkcanvas.pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)        

    # create axes
    ax1 = fig.add_subplot(1,2,1)
    ax1.set_ylim((-1, 10))
    ax1.set_xlabel('Time [$\mu$s]')
    ax1.set_ylabel('Magnitude ratio [linear]')
    ax1.grid()
    ax2 = fig.add_subplot(1,2,2)
    ax2.set_ylim((-200, 200))
    ax2.set_xlabel('Time [$\mu$s]')
    ax2.set_ylabel('Angle difference [deg]')
    ax2.grid()

    # add save button
    button_frame = Tk.Frame(master=root)
    button_frame.pack(side=Tk.TOP, anchor="w")
    add_stab_save_button(roach, button_frame)

    # get data
    mag_ratio, angle_diff = get_stab_data(roach)

    ax1.plot(time, mag_ratio)
    ax2.plot(time, angle_diff)

def add_stab_save_button(roach, button_frame):
    """
    Save the stability data into a file.
    """
    save_button = Tk.Button(button_frame, text="Save data")
    def save():
        mag_ratio, angle_diff = get_stab_data(roach)
        np.savez("stability_data", mag_ratio=mag_ratio,     
            angle_diff=angle_diff)
        print("Data saved")
    save_button.config(command=save)
    save_button.pack(side=Tk.LEFT)

def get_stab_data(roach):
    chnl_prim_real = cd.read_data(roach, bram_chnl0[0], 
        chnl_addr_width, chnl_word_width, chnl_data_type)
    chnl_prim_imag = cd.read_data(roach, bram_chnl0[1], 
        chnl_addr_width, chnl_word_width, chnl_data_type)
    chnl_ref_real  = cd.read_data(roach, bram_chnl1[0], 
        chnl_addr_width, chnl_word_width, chnl_data_type)
    chnl_ref_imag  = cd.read_data(roach, bram_chnl1[1], 
        chnl_addr_width, chnl_word_width, chnl_data_type)
    
    chnl_prim = chnl_prim_real + 1j*chnl_prim_imag
    chnl_ref  = chnl_ref_real  + 1j*chnl_ref_imag

    stab_data = chnl_ref / chnl_prim

    return np.abs(stab_data), np.angle(stab_data, deg=True)

if __name__ == "__main__":
    main()
