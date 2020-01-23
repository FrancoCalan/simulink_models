#!/bin/sh
plot_spectra.py \
    --ip        192.168.1.11 \
    --bof       kestfilt_2048ch_60mhz.bof \
    --bramnames dout0_0 dout1_0\
    --nspecs    2 \
    --dtype     ">u8" \
    --addrwidth 11 \
    --datawidth 64 \
    --bandwidth 60 \
    --nbits     8 \
    --countreg  cnt_rst \
    --accreg    acc_len \
    --acclen    $((2**10))

