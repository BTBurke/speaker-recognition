#!/usr/bin/env python

from mongoengine import *
from spkrec.db.schema import *
from spkrec.db.mongoengine_ext import *
import scikits.audiolab as audio

def speaker_test():
    spk = Speaker.objects.first()
    
    print 'Name: %s' % spk.name
    print 'Language: %s' % spk.language
    print 'Gender: %s' % spk.gender
    print 'Dialect: %s' % spk.dialect
    
    
def audio_test():
    aud = Audio.objects.first()
    
    print 'Frames: %i' % aud.frames
    print 'Encoding: %s' % aud.encoding
    print 'Rate: %i' % aud.rate
    print 'Channels: %i' % aud.ch
    print 'Speaker: %s' % Speaker.objects.with_id(aud.speaker).name
    print 'Filename: %s' % aud.filename
    print 'Speaker Name: %s' % aud.speaker_name
    
    fname_out = self_extract(aud.data, aud.filename+'.'+aud.encoding)
    sfile = audio.Sndfile(fname_out, 'r')
    sndvec = sfile.read_frames(aud.frames)
        
    audio.play(sndvec, aud.rate)  

    
if __name__ == '__main__':
    connect_to_database()
    print '---- Speaker Test ----'
    speaker_test()
    print '---- Audio Test ----'
    audio_test()