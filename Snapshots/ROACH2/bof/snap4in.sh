#!/bin/bash
plot_snapshots.py \
    --ip         192.168.1.12 \
    --bof        snap4in.bof.gz \
    --upload      \
    --snapnames  adcsnap0 adcsnap1 adcsnap2 adcsnap3 \
    --dtype      ">i1" \
    --nsamples   200
