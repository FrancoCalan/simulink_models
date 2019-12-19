#!/bin/sh
plot_snapshots.py \
    --ip         192.168.1.12 \
    --bof        snap2in.bof.gz \
    --rver       2 \
    --snapnames  adcsnap0 adcsnap1 \
    --dtype      ">i1" \
    --nsamples   200
