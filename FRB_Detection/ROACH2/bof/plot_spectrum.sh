#!/bin/bash
plot_spectra.py \
    --ip        192.168.1.12 \
    `#--bof       detector_roach2_v2_2.bof.gz` \
    --upload     \
    --bramnames spec0 spec1 spec2 spec3 spec4 spec5 spec6 spec7 \
    --nspecs    1 \
    --addrwidth 3 \
    --datawidth 64 \
    --bandwidth 540 \
    --nbits     8 \
    --countreg  cnt_rst \
    --accreg    acc_len \
    --acclen    $((2**10))
