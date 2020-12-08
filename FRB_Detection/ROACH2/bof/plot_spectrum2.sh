#!/bin/bash
plot_spectra.py \
    --ip        192.168.1.12 \
    `#--bof       frbd_64ch_600mhz.bof.gz` \
    --upload     \
    --bramnames spec0_0 spec0_1 spec0_2 spec0_3 \
    --nspecs    1 \
    --addrwidth 4 \
    --datawidth 32 \
    --bandwidth 600 \
    --nbits     8 \
    --countreg  cnt_rst \
    --accreg    acc_len \
    --acclen    $((2**10))
