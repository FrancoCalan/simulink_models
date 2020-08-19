#!/bin/bash
plot_snapshots.py \
    --ip         192.168.1.12 \
    `#--bof        kestfilt_4096ch_1080mhz.bof.gz` \
    --upload \
    --snapnames  adcsnap0 adcsnap1 \
    --dtype      ">i1" \
    --nsamples   200
