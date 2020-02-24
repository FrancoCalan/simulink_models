#!/bin/sh
plot_spectra.py \
    --ip        192.168.1.15 \
    --bof       mcs_1mch_70mhz.bof.gz \
    --upload     \
    --bramnames dout0_0 \
    --nspecs    1 \
    --addrwidth 8 \
    --datawidth 64 \
    --bandwidth 1080 \
    --nbits     8 \
    --countreg  cnt_rst \
    --accreg    acc_len \
    --acclen    $((2**10))
