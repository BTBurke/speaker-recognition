#!/usr/bin/env python
# schema.py
# Copyright Xemplar Biometrics, 2011
# 
# Establishes mongoDB schemas

from mongoengine import *
from mongoengine_ext import NumpyArrayField, SVMModelField

        
class Speaker(Document):
    #Unique name from the speech corpora, one entry per speaker
    name = StringField(required=True, unique=True)
    #Two-letter abbreviation for language
    language = StringField()
    #male/female
    gender = StringField()
    #String representing a particular dialect, i.e., American English
    dialect = StringField()
    #List of objectids corresponding to all audio files for speaker
    audiofiles = ListField(ObjectIdField())
    
class Audio(Document):
    #Number of samples * channels
    frames = IntField()
    #Wav, FLAC, AIFF
    encoding = StringField()
    #Samplerate in Hz
    rate = IntField()
    #File stored binary in GridFS
    data = FileField()
    #Number of channels
    ch = IntField()
    #Objectid of speaker entry
    speaker = ObjectIdField()
    #String of prompts for spoken words
    prompt = StringField()
    #Original filename
    filename = StringField()
    #Speaker's name as string
    speaker_name = StringField()
    
class Mfcc(Document):
    #File stored compress numpy array
    data = NumpyArrayField()
    #Energy in each window
    energy = NumpyArrayField()
    #Rows with 1 indicate detected speech
    energydetectorindex = NumpyArrayField()
    #ObjectId of audio record for original recording
    audio_parent = ObjectIdField()
    #ObjectId of speaker entry
    speaker = ObjectIdField()
    #Speaker's name as string
    speaker_name = StringField()
    #Configuration details from config collection
    config_details = ObjectIdField()
    
    
class Config(Document):
    #Name of external program used with config file
    external_program = StringField()
    #Dict of Attribute + Setting for use with write_config
    config_details = DictField()
    #Free form dict for metadata pertinent to config
    metadata = DictField()
    #Description of config details
    description = StringField()
    #Tags for config details
    tags = ListField(StringField())    
    
class Ubm(Document):
    #Number of minutes to train UBM
    train_mins = IntField()
    #Gender (male, female, mixed)
    train_gender = StringField()
    #UBM data
    ubm_weights = NumpyArrayField()
    ubm_means = NumpyArrayField()
    ubm_vars = NumpyArrayField()

class Model(Document):
    #UBM derived from
    base_ubm = ObjectIdField()
    #Speaker pointer
    speaker = ObjectIdField()
    #Speaker Name
    speaker_name = StringField()
    #Number of seconds of training data
    train_time = IntField()
    #Model data
    model_weights = NumpyArrayField()
    model_means = NumpyArrayField()
    #model_vars = NumpyArrayField()

class SV(Document):
    #Model derived from
    base_model = ObjectIdField()
    #Supervector
    sv = NumpyArrayField()
    #Speaker Name
    speaker_name = StringField()
    #Speaker ID
    speaker = ObjectIdField()
    #Included to enable random draws
    random = FloatField()

class SVM(Document):
    #Class parameters
    classifier = SVMModelField()
    #Speaker Name
    speaker_name = StringField()
    #Scale factor to divide unknown SV by
    scale_factor = FloatField()

class Test_results(Document):
    speaker_name = StringField()
    subject_instances = IntField()
    impostor_instances = IntField()
    correct = IntField()
    false_positive = IntField()
    false_negative = IntField()
    accuracy = FloatField()


