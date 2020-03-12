#!/bin/bash
plot_snapshots.py \
    --ip         133.40.220.2 \
    `#--bof        dss_2048ch_1520mhz.bof.gz` \
    `#--upload` \
    --snapnames  adcsnap0 adcsnap1 \
    --dtype      ">i1" \
    --nsamples   200
