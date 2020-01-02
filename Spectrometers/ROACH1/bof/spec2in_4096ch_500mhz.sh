#!/bin/sh
plot_spectra.py \
    --ip        192.168.1.11 \
    --bof       spec2in_4096ch_500mhz.bof \
    --rver      1 \
    --bramnames dout0_0 dout0_1 dout0_2 dout0_3 \
                dout1_0 dout1_1 dout1_2 dout1_3 \
    --nspecs    2 \
    --dtype     ">u8" \
    --addrwidth 9 \
    --datawidth 64 \
    --bandwidth 480 \
    --nbits     8 \
    --countreg  cnt_rst \
    --accreg    acc_len \
    --acclen    $((2**16))
