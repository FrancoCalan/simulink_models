import time
import corr, qdr
import numpy as np
import matplotlib.pyplot as plt
import calandigital as cd

def main():
    # initialize
    fpga = cd.initialize_roach('192.168.1.12', 'qdr_ct_test.bof.gz', uopload=True)
        
    # calibrate qdr
    my_qdr = cd.Qdr(fpga, 'qdr0')
    my_qdr.qdr_cal(fail_hard=True, verbosity=1)
    time.sleep(0.1)
    
    # read data
    fpga.write_int('qdr_en', 1)
    time.sleep(2)

    # create check data
    check_data = create_check_data()

    # create figure
    fig, line_orig, line_tran = create_figure()
    
    # check data in loop
    while True:
        # get data
        orig_data = np.frombuffer(fpga.read('original' , (2**8)*(2**8)*4, 0), dtype='>u4')
        tran_data = np.frombuffer(fpga.read('transpose', (2**8)*(2**8)*4, 0), dtype='>u4')
    
        # check data correctness
        if not np.array_equal(tran_data, check_data):
            print("ERROR: read data not equal to expected data!")
            print("Read data:")
            print(tran_data)
            print("Expected data:")
            print(check_data)

        # plot data
        line_orig.set_data(range(2**8), orig_data)
        line_tran.set_data(range(2**8), tran_data)
        fig.canvas.draw()


def create_check_data():
    rows  = 2**8    
    cols  = 2**8
    check_data = np.arange(rows*cols)
    check_data = np.reshape(check_data, (rows, cols))
    check_data = np.reshape(check_data.T, (1, rows*cols))[0]
    return check_data

def create_figure():
    fig, ax = plt.subplots(1, 1)
    fig.set_tight_layout(True)
    fig.show()
    fig.canvas.draw()

    ax.set_xlim((0, 2**8))
    ax.set_ylim((0, 2**8))
    ax.set_title("Original vs Transpose")
    ax.grid()
    ax.legend()

    line_orig = ax.plot([], [], '-', label='original')
    line_tran = ax.plot([], [], '-', label='transpose')

    return fig, line_orig, line_tran

if __name__ == "__main__":
    main()
