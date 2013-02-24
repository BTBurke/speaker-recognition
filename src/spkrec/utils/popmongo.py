#!/usr/bin/env python
# popmongo.py
# Copyright Xemplar Biometrics, 2011
# 
# Populates mongoDB with data from open source speech corpora

import re
from pprint import *
import os
import struct
import scikits.audiolab as audio
import numpy as np
from spkrec.db.girthy import create_connection
import uuid
import pymongo
import snappy
import pickle
import time
from gridfs import GridFS
from mongoengine import *
from spkrec.db.schema import Audio, Speaker
from spkrec.db.mongoengine_ext import connect_to_database
from clint.textui.progress import bar

def getconnection(dbname):
    #TODO: multiple connections for GridFS and mongoengine, reduce to one
    connect_to_database(dbname) #mongoengine database connection
    db = create_connection(database = dbname) #generic pymongo database connection
    dbfile = GridFS(db) #GridFS database connection
    return db, dbfile

def loopandinsert(db, dbfile):
    
    dirlist = tryopenfile('dirlist.txt')
    
    if not dirlist:
        assert False, 'Could not open directory list'
    
    dname = dirlist.readlines()
    
    # Set up processing variables
    prepend_dir = './uncompressed/'
    process_files = ['audiofile_details', 'README', 'PROMPTS'] 
    
    #Run preprocessing error check to see where files are missing, correct if necessary
    empty_lists = []
    for i in range(len(process_files)):
        empty_lists.append([])
    
    errors = dict(zip(process_files, empty_lists))
    
    for dirname in dname:
        dirname = dirname.rstrip()
        for pfile in process_files:
            fid = tryopenfile(prepend_dir + dirname + '/etc/' + pfile)
            if not fid:
                errors[pfile].append(dirname)
    total_records = len(dname)
    print '------- Error Summary ------'
    print 'Total Records: ', total_records
    for key in errors.keys():
        num_errors = len(errors[key])
        print key, num_errors, float(num_errors)/float(total_records)*100.0
    
    #Populate the database from files
    n=0
    total = len(dname)
        
    for dirname in bar(dname):
        dirname = dirname.rstrip()
        
        audiofile = {'rate': 0, 'bits': 0, 'type': ''}
        dlist = os.listdir(prepend_dir + dirname)
        for d in dlist:
            if d.lower() == 'etc' or d.lower() == 'license' or d.lower() == 'licence':
                pass
            else:
                audiofile['type'] = d.lower()
        
        for pfile in process_files:
            #process aux information in the files
            
            if dirname not in errors[pfile]:
                fid = tryopenfile(prepend_dir + dirname + '/etc/' + pfile)
                if not fid:
                    assert False, 'File not found despite error checking.'
                
                lines = fid.readlines()
                
                if pfile == 'audiofile_details':
                    audiofile = process_audiofile(lines, dirname, prepend_dir)
                if pfile == 'README':
                    readme = process_readme(lines, dirname)
                if pfile == 'PROMPTS':
                    prompts = process_prompts(lines)
        
        #insert empty list until audiofiles processed
        #readme['_id'] = str(uuid.uuid4())
        readme['audiofiles'] = []
        #print audiofile
        #print readme
        #print prompts
        
        #existing_record = db.speaker.find_one({'name': readme['name']})
        try:
            speaker_rec = Speaker.objects.get(name = readme['name'])
            #print existing_record
            spk_id = speaker_rec.id
        except Speaker.DoesNotExist:
            try:
                #spk_id = db.speaker.insert(readme)
                speaker_rec = Speaker()
                speaker_rec.name = readme['name']
                speaker_rec.audiofiles = []
                if 'language' in readme.keys():
                    speaker_rec.language = readme['language']
                if 'gender' in readme.keys():
                    speaker_rec.gender = readme['gender']
                if 'dialect' in readme.keys():
                    speaker_rec.dialect = readme['dialect']
                    
                    
                speaker_rec.save(safe=True)
                spk_id = speaker_rec.id
            except OperationError:
                assert False, "Error on insert to Speaker collection"    
            #except pymongo.errors.AutoReconnect:
            #    print db.error()
            #    print db.last_status()
        
        # read available voice samples          
        wavfiles = process_wavfiles(dirname, prepend_dir, audiofile['type'], readme['name'] , spk_id, db, prompts, dbfile)
        if not wavfiles:
            print wavfiles
            assert False, "no files returned"
        
        #print wavfiles
        #spk_id = db.speaker.insert({'name': readme['name'], 'language': readme['language'], 'gender': readme['gender'], 'dialect': readme['dialect'], 'audiofiles': []})
        if speaker_rec.audiofiles:
            old_wavfiles = speaker_rec.audiofiles
            if old_wavfiles:
                wavfiles.extend(old_wavfiles)
        
        speaker_rec.audiofiles = wavfiles
        
        try:
            speaker_rec.save(safe=True)
        except OperationError:
            assert False, "Updated insert failed"
#        try:
#            spk_id = db.speaker.find_and_modify({'_id': spk_id}, {'$set': {'audiofiles': wavfiles}})
#        except pymongo.errors.AutoReconnect:
#            print db.error()
#            print db.last_status()
        
        
        #n=n+1
        #print str(float(n)/float(total)*100.) + " Complete"
        
def process_audiofile(lines, dirname, prepend_dir):
    """Reads the audiofile_details format and returns sample rate and bits"""
    regex = r"[0-9A-Za-z]*.wav:([0-9]*)kHz-([0-9]*)bits"
    for line in lines:
        s = re.findall(regex, line)
    
    if s:
        audiofile = {'rate': int(s[0][0])*1000, 'bits': int(s[0][1])}
    else:
        audiofile = {'rate': 0, 'bits': 0}
    
    dlist = os.listdir(prepend_dir + dirname)
    for d in dlist:
        if d == 'etc' or d == 'LICENSE':
            pass
        else:
            audiofile['type'] = d.lower()
        
    
    return audiofile

def process_readme(lines, dirname):
    regex = [r"User (Name):([0-9A-Za-z]+)", r"(Gender):[\s]*([A-Za-z]+)", r"(Language):[\s]*([A-Za-z]*)", \
             r"Pronunciation (dialect):[\s]*([A-Za-z\s]*)"]
    readme = {}  
    for line in lines:
        line = line.rstrip()
        s = [re.findall(regex1, line) for regex1 in regex]
        if s:
            for l in s:
                if l:
                    readme[l[0][0].lower()] = l[0][1].lower()
    if not 'name' in readme.keys():
        regex = r"([A-Za-z0-9]+)-[A-Za-z0-9-]*"
        s = re.findall(regex, dirname)
        if s:
            readme['name'] = s[0].lower()
        else:
            readme['name'] = 'anonymous'
    
    return readme

def process_prompts(lines):
    regex = r"[-A-Za-z0-9]+/mfc/([-A-Za-z0-9]+)\s(['A-Za-z\s]*)"
    prompts = {}
    for line in lines:
        line = line.rstrip()
        s = re.findall(regex, line)
        if s:
            prompts[s[0][0].lower()] = s[0][1].upper()
    
    return prompts

def process_wavfiles(dirname, prepend_dir, audiotype, speaker_name, spk_id, db, prompts, dbfile):
    
    dirlist = os.listdir(prepend_dir + dirname + '/'+ audiotype + '/')
    wavfile_ids = []
    
    for fname in dirlist:        
        try:
            sfile = audio.Sndfile(prepend_dir + dirname + '/' + audiotype + '/' + fname, 'r')
        except:
            print prepend_dir, dirname, audiotype, fname
            assert False, "could not open soundfile"
        #print sfile.nframes, sfile.encoding, sfile.format, sfile.samplerate, sfile.channels, sfile.file_format
        #sndvec = sfile.read_frames(sfile.nframes)
        #sndvec_comp = sndvec.tolist()
        sndfile = open(prepend_dir + dirname + '/' + audiotype + '/' + fname, 'r')
        
        #print np.size(sndvec,0), np.size(sndvec,1)
        #audio.play(sndvec, sfile.samplerate) 
        
        if fname.split('.')[0] in prompts.keys():
            insert_prompt = prompts[fname.split('.')[0]]
        else:
            insert_prompt = ''
        
        #start = time.time()
        #try:
            #audio_id = db.audio.insert({'frames': sfile.nframes, 'encoding': sfile.encoding, 
            #                            'rate': sfile.samplerate, 'data': oid, 
            #                            'ch': sfile.channels, 'speaker': spk_id, #'type': sndvec.dtype.name,
            #                            'prompt': insert_prompt, 'filename': fname.split('.')[0], 'speaker_name': speaker_name})
        
        #except pymongo.errors.AutoReconnect:
        #    print db.error()
        #    print db.last_status()
        audio_rec = Audio()
        audio_rec.frames = sfile.nframes
        audio_rec.encoding = fname.split('.')[1]
        audio_rec.rate = sfile.samplerate
        audio_rec.data = sndfile
        audio_rec.data.content_type = 'audio/' + audiotype
        audio_rec.ch = sfile.channels
        audio_rec.speaker = spk_id
        audio_rec.prompt = insert_prompt
        audio_rec.filename = fname.split('.')[0]
        audio_rec.speaker_name = speaker_name
        
        try:
            audio_rec.save(safe=True)
            audio_id = audio_rec.id
        except OperationError:
            assert False, "Insert failed"
         
        if audio_id:
            wavfile_ids.append(audio_id)
        else:
            assert False, "Error on insert"
    return wavfile_ids
        
def tryopenfile(filename, wavfile=False):
    """Tries to open given filename (binary if wavfile=True).  Returns file id if successful, or False if not"""
    #print filename
    try:
        if wavfile:
            fid = open(filename, mode='rb')
        else:
            fid = open(filename)
        return fid
    except:
        return False

if __name__ == '__main__':
    db, dbfile = getconnection('spkrec')
    loopandinsert(db, dbfile)
    