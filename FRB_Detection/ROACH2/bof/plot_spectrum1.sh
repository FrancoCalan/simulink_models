#!/bin/bash
plot_spectra.py \
    --ip        192.168.1.12 \
    `#--bof       frbd_64ch_600mhz.bof.gz` \
    --upload     \
    --bramnames spec1_0 spec1_1 spec1_2 spec1_3 \
    --nspecs    1 \
    --addrwidth 4 \
    --datawidth 64 \
    --bandwidth 600 \
    --nbits     8 \
    --countreg  cnt_rst \
    --accreg    acc_len \
    --acclen    $((2**10))
