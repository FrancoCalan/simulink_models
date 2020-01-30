#!/bin/sh
plot_spectra.py \
    --ip        192.168.1.12 \
    --bof       dec_test.bof.gz \
    --upload     \
    --bramnames dout0_0 dout0_1 \
    --nspecs    2 \
    --dtype     ">u8" \
    --addrwidth 8 \
    --datawidth 64 \
    --bandwidth 1080 \
    --nbits     8 \
    --countreg  cnt_rst \
    --accreg    acc_len \
    --acclen    $((2**10))
