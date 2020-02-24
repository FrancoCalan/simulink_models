#!/bin/sh
plot_spectra.py \
    --ip        192.168.1.12 \
    --bof       spec2in_2048ch_1520mhz.bof.gz \
    --upload     \
    --bramnames dout0_0 dout0_1 dout0_2 dout0_3 dout0_4 dout0_5 dout0_6 dout0_7 \
                dout1_0 dout1_1 dout1_2 dout1_3 dout1_4 dout1_5 dout1_6 dout1_7 \
    --nspecs    2 \
    --addrwidth 8 \
    --datawidth 64 \
    --bandwidth 1080 \
    --nbits     8 \
    --countreg  cnt_rst \
    --accreg    acc_len \
    --acclen    $((2**16))
