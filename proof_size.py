#!/usr/bin/python
# -*- coding: UTF-8 -*-

import sys
import math

SECURITY_LEVEL=80
SIG_SIZE=4*SECURITY_LEVEL #ed25519

TOTAL_SIZE = 2 << 27
UPDATES_PER_DAY = int(TOTAL_SIZE * 0.01)
EPOCH_LENGTH_MINUTES = 10
EPOCHS_PER_DAY = (24 * 60 / EPOCH_LENGTH_MINUTES)
UPDATES_PER_EPOCH = (UPDATES_PER_DAY/EPOCHS_PER_DAY)

def proof_size(N, l):
  return (1 + math.ceil(math.log(N, 2))) * 2 * SECURITY_LEVEL + SIG_SIZE

f= int(proof_size(TOTAL_SIZE, SECURITY_LEVEL))
s= int(proof_size(UPDATES_PER_EPOCH, SECURITY_LEVEL))

daily_update_bits = (EPOCHS_PER_DAY - 1) * s + f
print "full proof sizes:", f/8, "bytes"
print "incremental proof sizes:", s/8, "bytes"
print "%.1f kB per day to audit" % ((daily_update_bits /8) / 1000.0)
