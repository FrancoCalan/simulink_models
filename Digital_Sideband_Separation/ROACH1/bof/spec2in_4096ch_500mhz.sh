#!/bin/sh
plot_spectra.py \
    --ip        192.168.1.11 \
    --bof       corr2in_1024ch_500mhz.bof \
    --rver      1 \
    --bramnames a2_0 a2_1 a2_2 a2_3 \
                b2_0 b2_1 b2_2 b2_3 \
    --nspecs    2 \
    --dtype     ">u8" \
    --addrwidth 8 \
    --datawidth 64 \
    --bandwidth 500 \
    --nbits     8 \
    --countreg  cnt_rst \
    --accreg    acc_len \
    --acclen    $((2**16))
