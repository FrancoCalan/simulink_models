#!/bin/sh
synchronize_adc5g.py \
    --ip             192.168.1.12 \
    --bof            corr2in_2048ch_1520mhz.bof.gz \
    --genip          192.168.1.34 \
    --genpow         -10 \
    --zdok0brams     dout_a2_0 dout_a2_1 dout_a2_2 dout_a2_3 \
                     dout_a2_4 dout_a2_5 dout_a2_6 dout_a2_7 \
    --zdok1brams     dout_b2_0 dout_b2_1 dout_b2_2 dout_b2_3 \
                     dout_b2_4 dout_b2_5 dout_b2_6 dout_b2_7 \
    --crossbramsreal dout_ab_re0 dout_ab_re1 dout_ab_re2 dout_ab_re3 \
                     dout_ab_re4 dout_ab_re5 dout_ab_re6 dout_ab_re7 \
    --crossbramsimag dout_ab_im0 dout_ab_im1 dout_ab_im2 dout_ab_im3 \
                     dout_ab_im4 dout_ab_im5 dout_ab_im6 dout_ab_im7 \
    --addrwidth      8 \
    --datawidth      64 \
    --bandwidth      1080 \
    --countreg       cnt_rst \
    --accreg         acc_len \
    --acclen         $((2**16)) \
    --delayregs      adc0_delay adc1_delay \
    --startchnl      1 \
    --stopchnl       2048 \
    --chnlstep       32 \
