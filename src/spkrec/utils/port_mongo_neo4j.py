#port mongo to neo4j
import random
import numpy as np

from spkrec.db.mongoengine_ext import connect_to_database
from spkrec.db.neo4j import NeoEngine
from spkrec.db.neo4j.NeoCustomType import *
from spkrec.db.schema import *
from spkrec.db.customtypes import *
from clint.textui.progress import bar

def port_speaker():
    print '---- Porting the Speaker database ----'
    db1 = connect_to_database()
    #db1.add_son_manipulator(TransformToBinary())

    # set up neo4j collection
    db = NeoEngine('/data/neo4j')

    db.create_collection('speaker')
    
    for speaker in bar(Speaker.objects):
        data = {'name': _udecode(speaker.name), 'gender': _udecode(speaker.gender),
                'language': _udecode(speaker.language),
                'dialect': _udecode(speaker.dialect)}
        node = db.insert('speaker', data)
    
    db.create_index('speaker', 'name')
    db.shutdown()

def test_port_speaker():
    print '---- Testing speaker database integrity ----'
    db1 = connect_to_database()
    db = NeoEngine('/data/neo4j')

    for speaker in bar(Speaker.objects):
        nodes = db.get('speaker', {'name': _udecode(speaker.name)})
        if len(nodes) > 1:
            print len(nodes)
            raise Exception, "Non-unique name in database"
        node = nodes.single

        for key in ['name', 'gender', 'language', 'dialect']:
            try:
                assert _udecode(speaker[key]) == node[key]
            except AssertionError:
                print "Failed (%s): %s" % (key, speaker.name)
    db.shutdown()

def port_sv():
    print '---- Porting the SV database ----'
    db1 = connect_to_database()
    db1.add_son_manipulator(TransformToBinary())    
    db = NeoEngine('/data/neo4j')

    db.create_collection('sv')

    cnt = db1.sv.find().count()
    cntidx = bar([i for i in range(cnt)])
    for sv in db1.sv.find():
        #print type(sv['sv'].value())
        cntidx.next()
        data = {'speaker_name': _udecode(sv['speaker_name']),
                'sv': sv['sv'].value(),
                'random': random.random()}
        node = db.insert('sv', data)
        
        # check data integrity
        try:
            assert _udecode(sv['speaker_name']) == db.get('sv', {'id': node['id']})['speaker_name']
            assert np.array_equal(sv['sv'].value(), NeoCustomType(node['sv']))
        except Exception:
            print sv['speaker_name']
            db.shutdown()
        
    db.create_index('sv', 'speaker_name')

    db.shutdown()

def _udecode(utf8):
    if isinstance(utf8, unicode):
        return str(utf8.decode('utf-8'))
    if isinstance(utf8, str):
        return utf8
    if not utf8:
        return ''

if __name__ == '__main__':
    port_speaker()
    test_port_speaker()
    port_sv()
