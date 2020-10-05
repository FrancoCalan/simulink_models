#!/bin/bash
plot_snapshots.py \
    --ip         192.168.1.12 \
    `#--bof        detector_roach2_v2_2.bof.gz` \
    --upload      \
    --snapnames  adcsnap0 \
    --dtype      ">i1" \
    --nsamples   200
