#!/bin/bash
calibrate_adc5g.py \
    --ip         133.40.220.2 \
    `#--bof        dss_2048ch_1520mhz.bof.gz` \
    `#--upload` \
    `#--genname    GPIB0::5::INSTR` \
    --genfreq    10 \
    --genpow     -3 \
    --zdok0snaps adcsnap0 \
    --zdok1snaps adcsnap1 \
    --do_mmcm \
    `#--do_ogp` \
    `#--do_inl` \
    --load_ogp \
    --load_inl \
    `#--plot_snap` \
    `#--plot_spec` \
    --nsamples   200 \
    --bandwidth  1080 \
    --loaddir    adc5gcal\ 2020-03-18\ 10:19:56
