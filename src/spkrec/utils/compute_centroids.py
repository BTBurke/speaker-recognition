import numpy as np
import csv

from spkrec.db.neo4j import NeoEngine
from spkrec.db.neo4j.NeoCustomType import NeoCustomType

def start_db(db_path='/data/neo4j'):
    db = NeoEngine(db_path)
    db.create_collection('centroids')
    return db

def _compute_centroid(db, speaker):
    
    cum = np.array([])
    
    for sv in db.get('sv', {'speaker_name': speaker['name']}):
        sv_data = NeoCustomType(sv['sv'])

        if not cum.any():
            cum = sv_data
            iteration = 1
        else:
            cum, iteration = update_centroid(sv_data, cum, iteration)
    
    centroid = cum / float(iteration)
    
    return centroid

def update_centroid(sv_data, cum, iteration):
    return cum+sv_data, iteration + 1


def write_node(db, speaker, centroid):

    data = {'speaker_name': speaker['name'],
            'centroid': centroid}

    node = db.insert('centroids', data)
    
    # Check write success
    assert np.array_equal(centroid, NeoCustomType(db.get('centroids',{'id': node['id']})))

def compute_centroids():
    db = start_db()
    for speaker in db.get('speaker'):
        centroid = _compute_centroid(db, speaker)
        print "%s complete" % speaker['name']
    db.shutdown()

if __name__ == '__main__':
    compute_centroids()
