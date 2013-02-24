#test_Concurrent_cursor.py
#
#

from mongoengine import *
from spkrec.db.schema import *
from spkrec.db.mongoengine_ext import connect_to_database
from spkrec.algorithm.concurrent_cursor import *
    
    
connected = connect_to_database()
if not connected:
    print 'SEARCHSTRATEGY: Could not connect to database'
    raise

cnt = Speaker.objects.count()

for concurrency in [64]:
    
    # test linear searching
    total_records = 0
    search = Concurrent_cursor(Speaker.objects())
    search.set_concurrency(concurrency)

    for i in range(concurrency):
        print "----Worker " + str(i+1) +"----"
        for record in search.search_path():
            print record.name
            total_records = total_records + 1
    search = False
    assert cnt==total_records


    # test random searching, no limit
    total_records = 0
    search = Concurrent_cursor(Speaker.objects(), strategy='random')
    search.set_concurrency(concurrency)

    for i in range(concurrency):
        print "----Worker " + str(i+1) +"----"
        for record in search.search_path():
            print record.name
            total_records = total_records + 1
    search = False
    assert cnt==total_records

    # test random searching, with limit
    lim = 100
    total_records = 0
    search = Concurrent_cursor(Speaker.objects(), strategy='random')
    search.set_concurrency(concurrency)

    for i in range(concurrency):
        print "----Worker " + str(i+1) +"----"
        for record in search.search_path(limit=lim):
            print record.name
            total_records = total_records + 1
    search = False
    assert lim==total_records

    # TODO: Test cursor error when more workers than concurrent settings
