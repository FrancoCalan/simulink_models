#!/bin/sh
plot_spectra.py \
    --ip        192.168.1.12 \
    --bof       spec4in_2048ch_600mhz.bof.gz \
    --rver      2 \
    --bramnames dout_0a_0 dout_0a_1 dout_0a_2 dout_0a_3 \
                dout_0c_0 dout_0c_1 dout_0c_2 dout_0c_3 \
                dout_1a_0 dout_1a_1 dout_1a_2 dout_1a_3 \
                dout_1c_0 dout_1c_1 dout_1c_2 dout_1c_3 \
    --nspecs    4 \
    --dtype     ">i8" \
    --addrwidth 9 \
    --datawidth 64 \
    --bandwidth 600 \
    --nbits     8 \
    --countreg  cnt_rst \
    --accreg    acc_len \
    --acclen    $((2**16))
