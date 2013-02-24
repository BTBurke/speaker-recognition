#!/usr/bin/env python
# queue_master.py
# Copyright Xemplar Biometrics, 2011
# 
# Worker processes, places work items in in-memory queue

import os
import beanstalkc
import time

def register_with_hq(ip=127.0.0.1):
    pass

def get_job():
    beanstalk = beanstalkc.Connection(host='localhost', port=11300)

    while True:
        job = beanstalk.reserve()
        if job:
            print str(os.getpid()) + ': ' + job.body
            time.sleep(.1)
            job.delete()

if __name__ == '__main__':
    
    print "I'm worker process: " + str(os.getpid())
    get_job()
    