#!/bin/bash
calibrate_adc5g.py \
    --ip         192.168.1.12 \
    `#--bof        frbd_64ch_600mhz.bof.gz` \
    --upload \
    `#--genname    TCPIP::192.168.1.34::INSTR` \
    --genfreq    10 \
    --genpow     -3 \
    --zdok0snaps adcsnap0 adcsnap0 \
    --do_mmcm \
    `#--do_ogp` \
    `#--do_inl` \
    --load_ogp \
    --load_inl \
    --plot_snap \
    --plot_spec \
    --nsamples   200 \
    --bandwidth  600 \
    --loaddir    adc5gcal\ 2020-01-09\ 15:31:42
