# mongoengine_ext.py
#
# Extends mongoengine field classes to include a compressed Numpy array field.
# Uses Google's Snappy compression engine for speedy compression/decompression.
#
# Implements a self-extracting GridFS 
# Copyright 2011, Xemplar Biometrics, Inc.

from mongoengine import *
from mongoengine.base import BaseField
from pymongo import Connection

import pymongo.binary
import snappy
from numpy import ndarray
import pickle
import gridfs
from scikits.learn import svm
from spkrec.db.customtypes import *

class NumpyArrayField(BaseField):
    """A Numpy array field with optional compression
       via Google's Snappy compression engine
    """
    def __init__(self, compression=True, **kwargs):
        self.compression = compression
        super(NumpyArrayField, self).__init__(**kwargs)
    
    def to_mongo(self, value):
        value_pickled = pymongo.binary.Binary(pickle.dumps(value, protocol=2))
        if self.compression:
            return pymongo.binary.Binary(snappy.compress(value_pickled))
        else:
            return value_pickled
    
    def to_python(self, value):
        if self.compression:
            value_uncompressed = snappy.uncompress(value)
            return pickle.loads(value_uncompressed)
        else:
            return pickle.loads(value)
    
    def validate(self, value):
        assert isinstance(value, ndarray)

class SVMModelField(BaseField):
    """
    A schema to store instances of SVM models from 
    the scikits.learn package
    """
    def __init__(self):
        super(SVMModelField, self).__init__()
    
    def to_mongo(self, value):
        value_pickled = pymongo.binary.Binary(pickle.dumps(value, protocol=2))
        return value_pickled
    
    def to_python(self, value):
        return pickle.loads(value)
    
    def validate(self, value):
        if isinstance(value, type(svm.SVC())) or isinstance(value, type(svm.LinearSVC())):
            pass
        else:
            assert False, "SVMModelField: Improper type."

        
def self_extract(gridfs_file, filename=None, directory='/tmp/'):
    """
    Extracts file from GridFS instance and saves to new file
    
    Usage: self_extract(gridfs_file, filename=None, directory='/tmp')
    Returns: path to file
    
    If no filename is supplied, generates a uuid4 filename with no extension
    """
    if not filename:
        import uuid
        filename = str(uuid.uuid4())
    
    try:
        data = gridfs_file.read()
    except Exception, e:
        print e
        raise
    
    with open(directory + filename, 'w') as fid:
        fid.write(data)
        fid.close()
        return directory + filename
            
def connect_to_database(db='spkrec', enable_customtypes=True):
    #To connect via mongoengine
    try:
        connect(db)
    except Exception, e:
        #TODO: Find what exceptions this throws and how to do connection pooling
        print e
        assert False
    
    #Also return connection via Pymongo and enable custom type conversions
    #if enable_customtypes is True
    print db
    c = Connection()
    db_conn = c[db]
    #db_conn.add_son_manipulator(TransformToBinary())
       
    return db_conn
    