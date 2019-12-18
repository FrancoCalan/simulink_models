#!/bin/sh
IP="192.168.1.11"
BOF="snap2in.bof"
RVER=1
ADCSNAP="adcsnap"
NSNAPSHOTS=2
DTYPE=">i1"
NSAMPLES=200

plot_snapshots.py \
    --ip   $IP \
    --bof  $BOF \
    --rver $RVER \
    -sn    $ADCSNAP \
    -ns    $NSNAPSHOTS \
    -dt    $DTYPE \
    -sa    $NSAMPLES
