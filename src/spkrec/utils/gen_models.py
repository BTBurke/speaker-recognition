#gen_models.py
#
# Generates MAP-adapted models for everthing in database
# Inputs: number of seconds of data for MAP adaptation

from spkrec.db.schema import *
from spkrec.db.mongoengine_ext import connect_to_database
#from spkrec.algorithm.concurrent_cursor import *
#from spkrec.algorithm.energydetector import strip_silence
from spkrec.algorithm.map_adapt import convert_type_db_gmm
from spkrec.utils.map_adapt_concurrent import map_adapt_concurrent, create_SV_from_GMM
#from scikits.learn import mixture
from celery.task import task
import numpy as np
from time import sleep


def map_adapt_all_models(t, CONCURRENCY):
        
    u = Ubm.objects.first()
    print "Im here"
    world = convert_type_db_gmm(u)
    
    #child = []
    for i in range(CONCURRENCY):
        print "Launching " + str(i)
        map_adapt_concurrent.delay(t, world, i, CONCURRENCY)

    #while not child.ready.all():
    #    sleep(5)
    
def convert_to_SV(CONCURRENCY=2):
    
    for i in range(CONCURRENCY):
        print "Launching " + str(i)

        create_SV_from_GMM.delay(i, CONCURRENCY)
           

if __name__ == '__main__':
    
    connected = connect_to_database()
    if not connected:
        print 'MAPADAPT: Could not connect to database'
        raise

    #map_adapt_all_models(2,1)
    convert_to_SV(CONCURRENCY=1)
