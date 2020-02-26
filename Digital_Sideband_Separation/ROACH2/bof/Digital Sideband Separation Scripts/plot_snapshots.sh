#!/bin/sh
plot_snapshots.py \
    --ip         192.168.1.12 \
    `#--bof        dss_2048ch_1520mhz.bof.gz` \
    `#--upload` \
    --snapnames  adcsnap0 adcsnap1 \
    --dtype      ">i1" \
    --nsamples   200
