#!/usr/bin/env python
# process_monitorUI.py
# Copyright Xemplar Biometrics, 2011
# 
# Monitors processes via zeroMQ comm channels outputs via textUI

from clint.textui import progress
from clint.textui import puts, colored
from clint.textui import columns
import random
import os
import time

col1 = 5
col2 = 30
col3 = 5
col4 = 30

while True:
    puts(columns([(colored.red('Core')),col1], [('Load'),col2], [colored.red('Core'),col3], ['Load', col4]))
    for l in range(32):
        puts(columns([(colored.red(str(l+1))), col1], [('>'*random.randint(0,29)),col2], [colored.red(str(l+33)),col3], ['>'*random.randint(0,29),col4]))
    time.sleep(.5)
    os.system('clear')