#!/bin/bash
plot_spectra.py \
    --ip        192.168.1.12 \
    --bof       spec2in_4096ch_1080mhz.bof.gz \
    --upload     \
    --bramnames dout0_0 dout0_1 dout0_2 dout0_3 dout0_4 dout0_5 dout0_6 dout0_7 \
    --nspecs    1 \
    --addrwidth 9 \
    --datawidth 64 \
    --bandwidth 540 \
    --nbits     8 \
    --countreg  cnt_rst \
    --accreg    acc_len \
    --acclen    $((2**16))
