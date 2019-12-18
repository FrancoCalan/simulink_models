#!/bin/sh
IP="192.168.1.13"
BOF="snap16in.bof.gz"
RVER=2
ADCSNAP="adcsnap"
NSNAPSHOTS=16
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
