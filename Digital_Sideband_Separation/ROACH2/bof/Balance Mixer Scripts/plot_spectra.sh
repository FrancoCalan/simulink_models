#!/bin/sh
plot_spectra.py \
    --ip        192.168.1.12 \
    --bof       spec2in_2048ch_1520mhz.bof.gz \
    `#--upload` \
    --bramnames dout_a2_0 dout_a2_1 dout_a2_2 dout_a2_3 dout_a2_4 dout_a2_5 dout_a2_6 dout_a2_7 \
                dout_b2_0 dout_b2_1 dout_b2_2 dout_b2_3 dout_b2_4 dout_b2_5 dout_b2_6 dout_b2_7 \
    --nspecs    2 \
    --addrwidth 8 \
    --datawidth 64 \
    --bandwidth 1080 \
    --nbits     8 \
    --countreg  cnt_rst \
    --accreg    acc_len \
    --acclen    $((2**16))
