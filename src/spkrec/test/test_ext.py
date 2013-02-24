#!/usr/bin/env python

from mongoengine import *
from mongoengine_ext import NumpyArrayField, self_extract

def connect_to_database(db='test'):
    try:
        connect(db)
    except Exception:
        #TODO: Find what exceptions this throws and how to do connection pooling
        assert False
        
    return True

class Test(Document):
    data = FileField()



if __name__ == '__main__':
    import numpy as np
    
    connect_to_database(db='test')

    data = np.ones((100,100), np.float)
    
    np.save('test.npy', data)
    
    test = Test()
    test.data = open('test.npy', 'r')
    test.data.filename = 'test3.npy'
    test.save()
    id = test.id
    
    test2 = Test.objects.with_id(id)
    filename = self_extract(test2.data)
    print filename
    