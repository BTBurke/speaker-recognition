import pymongo
from pymongo import Connection
from subprocess import call
from boto.s3.connection import S3Connection
from boto.s3.key import Key
import tarfile
import datetime
import numpy as np
import snappy
import pickle
from pymongo.son_manipulator import SONManipulator

#from pymongo.collection import Collection
#import numpy as np


def create_connection(host='localhost',port=27017, database=None):
    """
    Usage: create_connection(host='localhost', port=27017, database=None)
    
    Opens connection to MongoDB and handles connection errors.
    
    Specifying database will return object connected to that database, otherwise
    database should be configured in application as db=connection['<database>']
    """
    
    try:
        connection = Connection(host,port,network_timeout=10)
    except pymongo.errors.ConnectionFailure:
        assert False, 'Could not get database connection.  Check mongod running.'
        
    if not database:
        return connection
    else:
        db = connection[database]
        return db
    

def mongodump(db='ALL', collection='ALL', tar=True):
    """
    Usage: mongodump(db='ALL', collection='ALL', tgz=True)
    
    Dumps entire database or specified collection to ./dump/<db>/<collection>.bson
    
    tar=True puts contents in a tarred file in the local directory 
    (filename = <db>-<collection>-YY.MM.DD-HHMM.tgz)
    """
    
    if db == 'ALL' and collection == 'ALL':
        print 'Calling mongodump'
        call(['mongodump'])
        outfile = './dump/'
    elif (db == 'ALL' and collection != 'ALL') or (db != 'ALL' and collection == 'ALL'):
        assert False, "Must specify both database and collection."
    else:
        print 'Calling mongodump with arguments'
        call(['mongodump', '-db', db, '-collection', collection ])
        outfile = './dump/' + db + '/' + collection + '.bson'
    
    if tar:
        fname = db + '-' + collection + '-' + datetime.datetime.now().strftime('%y.%m.%d-%H%M') + '.tgz'
        tfile = tarfile.open(fname, 'w:gz')
        print 'Addding file or directory: ' + outfile 
        tfile.add(outfile)
        tfile.close()
        call(['rm', '-rf', './dump/'])
        return fname
    else:
        return None


def s3upload(file_to_upload, bucket='xemplar-mongo'):
    conn = S3Connection('AKIAIEHCIR6NT7HX3XZA', '7LuTB0l8osyhaaF8yHydhdECkW+SYaU9rMI/6p+e')
    b = conn.get_bucket(bucket)
    k = Key(b)
    k.key = file_to_upload
    k.set_contents_from_filename(file_to_upload, reduced_redundancy=True)
    call(['rm', '-rf', file_to_upload])

    
if __name__ == '__main__':
    create_connection()
    tfile = mongodump()
    s3upload(tfile)
    
    #mongodump()