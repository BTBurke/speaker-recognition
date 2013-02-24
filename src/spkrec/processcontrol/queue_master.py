#!/usr/bin/env python
# queue_master.py
# Copyright Xemplar Biometrics, 2011
# 
# Spawns worker processes, places work items in in-memory queue

import subprocess
import beanstalkc
import time

def launch_workers(N=3):
    
    worker_pids=[]
    for i in range(N):
        w_pid = subprocess.Popen('./queue_worker.py')
        if w_pid:
            worker_pids.append(w_pid)
        else:
            assert False, "Failed to launch process"
    return worker_pids

if __name__ == '__main__':
    
    beanstalk = beanstalkc.Connection(host='localhost', port=11300)
    worker_pids = launch_workers()
    
    for i in range(50):   
        beanstalk.put(str(i))

    while beanstalk.peek_ready():
        time.sleep(1)

    for w_pid in worker_pids:
        w_pid.kill()
    
    beanstalk.close()
    
    