#!/usr/bin/env python
#energydetector.py
#
# GMM to classify speech vs silence from energy in each audio frame
#
# Copyright 2011, Xemplar Biometrics Inc

from scikits.learn import mixture 
import numpy as np

def classify_speech(energy):
    """ Trains a two mixture GMM based on the energy component in each frame.
    
    Usage: energy_segmentation = classify_speech(energy)
    
    Inputs:
    energy -- Numpy array of energy in each frame
    
    Outputs:
    energy_segmentation -- Numpy array of detected speech (1=speech, 0=silence)
    """
    
    
    g = mixture.GMM(n_states=2)
    g.fit(energy)
    
    #Higher energy indicates speech, location in GMM mean
    #vector can vary based on initial conditions
    if g.means[0] > g.means[1]:
        energy_tag = 0
        silence_tag = 1
    else:
        energy_tag = 1
        silence_tag = 0
    
    speech_predict = g.predict(energy)
    
    #Return 1 where speech detected, 0 otherwise
    energy_segmentation = np.zeros(np.shape(energy), dtype=np.int)
    energy_segmentation[speech_predict==energy_tag] = 1
    energy_segmentation[speech_predict==silence_tag] = 0
    
    return energy_segmentation

def strip_silence(mfcc, energyindex):
    
    try:
        speech_indices, temp = np.where(energyindex==1)
    except ValueError:
        #Return empty array on no speech
        return np.array([])
    mfcc_speech = mfcc[speech_indices,:]
    return mfcc_speech

def process_db_energy():
    """
    Train new GMM for each audio cut in database, label each window, 
    and return index for speech-containing frames
    """
    from clint.textui.progress import bar
    from spkrec.db.schema import Mfcc
    from spkrec.db.mongoengine_ext import connect_to_database
    
    
    connected = connect_to_database()
    if not connected:
        print 'ENERGYDETECTOR: Could not connect to database'
        raise
    
    #Hack to prevent DB cursor from timing out
    cnt = Mfcc.objects.count()
    ind = np.floor(np.linspace(0,cnt,15))
    
    for i in range(0,len(ind)-1):
        for mfcc in bar(Mfcc.objects[ind[i]:ind[i+1]]):
            
            energy_vec = np.reshape(mfcc.energy, (np.size(mfcc.energy,0),1))
            
            detected_speech = classify_speech(energy_vec)
            
            mfcc.energydetectorindex = detected_speech
            mfcc.save(safe=True)

if __name__ == '__main__':
    process_db_energy()
    
    
    