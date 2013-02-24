#!/usr/bin/env python
# mfcc.py
#
# Computes MFCCs
#
# Copyright 2011, Xemplar Biometrics Inc.


import subprocess
import os
import logging
import uuid
from spkrec.algorithm.yaafelib import *
from spkrec.algorithm.yaafelib.yaafefeatures import *
from scikits.audiolab import Sndfile
import numpy as np
import matplotlib.pyplot as plt
import struct

def calculate_mfcc_spro(infile, outfile, samplerate, numcoefs=12, numfilters =24, timewindow=20, overlap=10, energy=True, normalize=True):
    """
    Calculates Mel-Frequency Cepstrum Coefficients (MFCCs) using the SPro4 library.
    
    Usage: calculate_mfcc(infile, outfile, samplerate, numcoefs=12, numfilters =24, timewindow=20, overlap=10, energy=True, normalize=True)
    """
        
    if numfilters < numcoefs:
        logging.warn("Number of filters < number of coefficients.  Making filters 2X coefficients for safety.")
        numfilters = 2 * numcoefs
        
    #check for ability to open input file
    try:
        fid = open(infile, 'r')
        fid.close()
    except IOError:
        logging.error('Input file does not exist - %s', infile)
        return False

    #check for SPro4 sfbcep executable    
#    if not os.access('sfbcep', os.R_OK):
#        logging.error('sfbcep is not properly installed in OS executable path or permissions not ok.')
#        return False
    
    if normalize:
        NORMALIZE_MEAN = '--cms'
        NORMALIZE_VAR = '--normalize'
    else:
        NORMALIZE_MEAN = NORMALIZE_VAR = ''
        
    if energy:
        ENERGY_CALC = '--energy'
    else:
        ENERGY_CALC = ''
    
    
    cmdline = ['sfbcep', NORMALIZE_MEAN, NORMALIZE_VAR, '--mel', '--num-filter=' + str(numfilters)]
    cmdline += ['-p', str(numcoefs), '-b', '512', ENERGY_CALC, infile, outfile ]
    
    cmdline = [cmd for cmd in cmdline if cmd]
    
    #print cmdline
    subprocess.Popen(cmdline)
      
    return outfile

#def calculate_mfcc(infile, samplerate, numcoefs=12, numfilters =24, timewindow=20, overlap=10):
#    """
#    Calculates Mel-Frequency Cepstrum Coefficients (MFCCs) using the YAAFE library.
#    
#    Usage: calculate_mfcc(infile, outfile, samplerate, numcoefs=12, numfilters =24, timewindow=20, overlap=10, energy=True, normalize=True)
#    """
#        
#    if numfilters < numcoefs:
#        logging.warn("Number of filters < number of coefficients.  Making filters 2X coefficients for safety.")
#        numfilters = 2 * numcoefs
#        
#    #check for ability to open input file
#    try:
#        sfile = Sndfile(infile, 'r')
#    except Exception, e:
#        logging.error('Input file does not exist - %s', infile)
#        print e
#        return False
#
#    #sndvec = sfile.read_frames(sfile.nframes)
#    #sndvec = np.reshape(sndvec, (1,sfile.nframes))
#    
#    #sndlength = np.size(sndvec)
#    
#    #Set up MFCC processing
#    block_size = int(float(timewindow) * 10.**(-3) / (1./float(sfile.samplerate)))
#    step_size = block_size / 2
#    
#    fp = FeaturePlan(sample_rate = sfile.samplerate)
#    
#    feat1 = 'mfcc: MFCC blockSize=' + str(block_size) + ' stepSize=' + str(step_size)
#    feat1 += ' CepsNbCoeffs=' + str(numcoefs) + ' CepsIgnoreFirstCoeff=0' + ' FFTWindow=Hamming'
#    feat1 += ' MelMaxFreq=' + str(sfile.samplerate/2) + ' MelMinFreq=20' + ' MelNbFilters=' + str(numfilters)
#    
#    ret = fp.addFeature(feat1)
#    if not ret:
#        print "Adding feature failed: %s" % feat1
#        raise
#    
#      
#    df = fp.getDataFlow()
#    #logging.info(df.display())
#    
#    engine = Engine()
#    ret = engine.load(fp.getDataFlow())
#    if not ret:
#        print "Failed to load dataflow in engine: %s" % fp.getDataFlow()
#        raise
#    
#    return_array=np.array([])
#    #feats = engine.processAudio(sndvec)
#    num_blocks = int(sfile.nframes / block_size / 2)
#    num_blocks = 3
#    print num_blocks
#    blocks = np.floor(np.linspace(0,sfile.nframes-1, num_blocks))
#    
#    #Begin buffer processing
#    engine.reset()
#    for (ind_start, ind_stop) in zip(blocks[0:-1], blocks[1::]):
#        #print 'test'
#        #print ind_start
#        print ind_stop
#        #print ind_stop-ind_start
#        #print sfile.nframes
#        sndvec = sfile.read_frames(int(ind_stop-ind_start))
#        sndvec = np.reshape(sndvec, (1, np.size(sndvec)))
#        #print sndvec
#        engine.writeInput('audio', sndvec)
#        engine.process()
#        feats = engine.readAllOutputs()
#        #print feats
#        if np.size(feats['mfcc'])>0:
#            #print feats['mfcc']
#            np.append(return_array, feats['mfcc'])
#            print return_array
#    engine.flush()
#    feats = engine.readAllOutputs()
#    if feats['mfcc'].any():
#        np.append(return_array, feats['mfcc'])
#        
#    
#    #print np.size(feats['mfcc'],0), np.size(feats['mfcc'],1)
#    #return_array = np.array(feats['mfcc'])
#    sfile.close()
#    print np.shape(return_array)
#    return return_array

#def calculate_energy(infile, samplerate, timewindow, overlap):
#    try:
#        sfile = Sndfile(infile, 'r')
#    except Exception, e:
#        logging.error('Input file does not exist - %s', infile)
#        print e
#        return False
#
#    sndvec = sfile.read_frames(sfile.nframes)
#    sndvec = np.reshape(sndvec, (1,sfile.nframes))
#    
#    
#    #Set up energy processing
#    block_size = int(float(timewindow) * 10.**(-3) / (1./float(sfile.samplerate)))
#    step_size = block_size / 2
#    
#    fp = FeaturePlan(sample_rate = sfile.samplerate)
#    
#    feat1 = 'energy: Energy blockSize=' + str(block_size) + ' stepSize=' + str(step_size)
#    ret = fp.addFeature(feat1)
#    if not ret:
#        print "Adding feature failed: %s" % feat1
#        raise
#    
#      
#    df = fp.getDataFlow()
#    #logging.info(df.display())
#    
#    engine = Engine()
#    ret = engine.load(fp.getDataFlow())
#    if not ret:
#        print "Failed to load dataflow in engine: %s" % fp.getDataFlow()
#        raise
#    
#    feats = engine.processAudio(sndvec)
#    
#    sfile.close()
#    return_array = np.array(feats['energy'])
#    
#    return return_array

#def normalize(feats, variance=False):
#    cepmeans = np.mean(feats,1)
#    cepstd = np.std(feats,1)
#    
#    for i in range(np.size(feats,0)):
#        feats[i,:] = feats[i,:] - cepmeans[i]
#        if variance:
#            feats[i,:] = feats[i,:] / cepstd[i]
#    
#    return feats

def read_spro4(infile, numceps, energy):
    
    #wait for flush to file
    while os.path.getsize(infile) < 1:
        pass
    
    try:
        fid = open(infile, 'rb')
    except IOError:
        logging.error('Could not open %s' % infile)
        raise
    
    #skip the SPRO4 14 byte header
    fid.seek(14)
    
    if energy:
        numrows = (os.path.getsize(infile)-14) / 4 / (numceps + 1)
    else:
        numrows = (os.path.getsize(infile)-14) / 4 / numceps
    
    if energy:
        arraylen = numceps + 1
    else:
        arraylen = numceps
        
    return_array = np.zeros((numrows, arraylen), dtype=np.float)
    for i in range(numrows):
        a = np.zeros(arraylen, dtype=np.float)
        for j in range(arraylen):
            a[j], = struct.unpack('<f', fid.read(4))
        return_array[i,:] = a
        
    fid.close()
    if energy:
        return_dict = {'mfcc': return_array[:,:-1], 'energy': return_array[:,-1]}
    else:
        return_dict = {'mfcc': return_array, 'energy': []}
    
    return return_dict

def spro_to_txt(dir):
    
    dirlist = os.listdir(dir + '*.mfcc')
    for infile in dirlist:
        outfile = infile.split('.')[0] + '.txt'
        cmdline = ['scopy', '-o', 'ascii', infile, outfile]
        subprocess.Popen(cmdline)
    return True

if __name__ == '__main__':
    # if run stand-alone, run all records in database
    logging.basicConfig(filename='mfcc.log', level=logging.DEBUG)
    
    from mongoengine import *
    from spkrec.db.schema import *
    from spkrec.db.mongoengine_ext import self_extract, connect_to_database
    from clint.textui.progress import bar
    
    connect_to_database()
    
    tag = 'initial'
    try:
        configs = Config.objects.get(tags=tag,external_program='sfbcep')
        #print configs.config_details
    except Config.DoesNotExist:
        #if not already an inital config entry, put in sane defaults
        cfg = {'numcoefs': 13, 'numfilters': 26, 'timewindow': 20, 'overlap': 10, 'energy': True, 'normalize': True}
        configs = Config()
        configs.config_details = cfg
        configs.external_program = 'sfbcep'
        configs.tags = [tag]
        configs.description= 'Initial population of the MFCC database; 20ms, 10ms overlap, normalized, energy.'
        configs.save(safe=True)
    
    import numpy as np
    cnt = Audio.objects.count()
    ind = np.floor(np.linspace(0,cnt,15))
    for i in bar(range(0,len(ind)-1)):
        #print ind[i]    
        
        for audio in bar(Audio.objects[ind[i]:ind[i+1]]):
            
            #print audio
            #logging.info('Processing %s' % audio.id)
            # Extract audio from GridFS and save in temp file
    
            dir = '/tmp/'
            fname = str(uuid.uuid4())
            fname_in = fname + '.' + audio.encoding
            fname_out = dir + fname + '.mfcc'
            fname_ext = self_extract(audio.data, filename=fname_in, directory=dir)
            
            # Compute MFCCs using YAAFE
            sets = configs.config_details
            outfile = calculate_mfcc_spro(fname_ext, fname_out, audio.rate, numcoefs=sets['numcoefs'], numfilters=sets['numfilters'], timewindow=sets['timewindow'], overlap=sets['overlap'], energy=sets['energy'], normalize=sets['normalize'])
    
            #delay while file writes to disk to avoid race condition
            while not os.path.isfile(outfile):
                pass
            
            return_dict = read_spro4(outfile, sets['numcoefs'], sets['energy'])
            
            
            # Save in database
            mfcc = Mfcc()
            mfcc.data = return_dict['mfcc']
            mfcc.energy = return_dict['energy']     
            mfcc.audio_parent = audio.id
            mfcc.speaker = audio.speaker
            mfcc.speaker_name = audio.speaker_name
            mfcc.config_details = configs.id
            
            mfcc.save(safe=True)
            if not mfcc.id:
                print "DB Failed Insert"
                raise
            
    #        test_insert = Mfcc.objects.with_id(mfcc.id)
    #        print np.shape(test_insert.data)
    #        print np.shape(test_insert.energy)
    #        print test_insert.audio_parent
    #        print test_insert.speaker
    #        print test_insert.speaker_name
    #        print test_insert.config_details
            
            