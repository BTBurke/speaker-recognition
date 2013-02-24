#!/usr/bin/env python
# monitor.py
# Copyright Xemplar Biometrics, 2011
# 
# Monitors processes via zeroMQ comm channels

import subprocess

# Launch textUI to monitor process statistics
pid_window = subprocess.Popen(['gnome-terminal', '--geometry', '80x34', '-x', 'python', 'process_monitorUI.py'])
