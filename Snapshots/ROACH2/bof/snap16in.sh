#!/bin/sh
plot_snapshots.py \
    --ip         192.168.1.12 \
    --bof        snap16in.bof.gz \
    --rver       2 \
    --snapnames  snap_a1 snap_a2 snap_a3 snap_a4 \
                 snap_b1 snap_b2 snap_b3 snap_b4 \
                 snap_c1 snap_c2 snap_c3 snap_c4 \
                 snap_d1 snap_d2 snap_d3 snap_d4 \
    --dtype      ">i1" \
    --nsamples   200
