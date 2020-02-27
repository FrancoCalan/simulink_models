#!/bin/bash
plot_snapshots.py \
    --ip         192.168.1.11 \
    --bof        snap2in.bof\
    --snapnames  adcsnap0 adcsnap1 \
    --dtype      ">i1" \
    --nsamples   200
