# train_ubm.py
#
# Copyright 2011, Xemplar Biometrics Inc

import numpy as np
from scikits.learn import mixture
from math import log
import logging

def train_gmm(obs, world=None, params={'num_mixtures': 1024}):
    """ Trains a GMM using N mixtures from given observations.
    
    Usage:  world = train_gmm(obs, world, params)
    
    Inputs:
    obs -- MxN Numpy array of observations (M observations to be clustered in N-dimensional space)
    world -- Previous world model to use for initialization (if not supplied, will initialize automagically)
    params -- {'num_mixtures': X} Use X mixtures in model, defaults to 1024
    
    Outputs:
    world -- GMM class output (contains means, weights, covars)
    """    
    
    if log(params['num_mixtures'],2) % 1:
        logging.warn('Number of mixtures not power of 2.  Will run slow.')
    
    if not world:
        world = mixture.GMM(n_states=params['num_mixtures'])
        world.fit(obs)
    else:
        world.fit(obs, init_params='')
    
    return world

def create_ubm(mins=.2):
    
    from clint.textui.progress import bar
    from spkrec.db.schema import Mfcc
    from spkrec.db.mongoengine_ext import connect_to_database
    from energydetector import strip_silence
    from pprint import pprint
    
    MIN_MINUTES = mins
    
    connected = connect_to_database()
    if not connected:
        print 'CREATE_UBM: Could not connect to database'
        raise
    
    #Hack to prevent DB cursor from timing out
    cnt = Mfcc.objects(__raw__={'speaker_name': 'anonymous'}).count()
    ind = np.floor(np.linspace(0,cnt,15))
    obs = np.array([])
    
    for i in range(0,len(ind)-1):
        for mfcc in bar(Mfcc.objects[ind[i]:ind[i+1]]):
            
            # Strip silence from MFCCs
            mfcc_speech = strip_silence(mfcc.data, mfcc.energydetectorindex)
            
            # Check for silent recordings and skip if found
            if not mfcc_speech.any():
                continue
            
            # Concatenate new speech data to end of observation array
            if not obs.any():
                obs = mfcc_speech
            else:
                obs = np.concatenate((obs,mfcc_speech),0)
            
            if np.size(obs,0) > (MIN_MINUTES * 60 / .01):
                break
            
        if np.size(obs,0) > (MIN_MINUTES * 60 / .01):
            break
    
    world = train_gmm(obs,params={'num_mixtures': 1024})
    pprint(np.shape(world.means))
    pprint(np.shape(world.weights))
    pprint(np.shape(world.covars))
    return world      
        
if __name__ == '__main__':
#    from timeit import Timer
#    time_results = []
#    for mins in [.2, .5, 1, 2, 5]:
#        exec_func = "create_ubm(" + str(mins) +")"
#        t= Timer(exec_func, "from __main__ import create_ubm")
#        time_results.append(t.timeit(number=1))
#        print time_results
#        
#    time_results = np.array(time_results)
#    np.save('timing', time_results)
    world = create_ubm(30.0)
    np.save('means', world.means)
    np.save('weights', world.weights)
    np.save('covars', world.covars)
    