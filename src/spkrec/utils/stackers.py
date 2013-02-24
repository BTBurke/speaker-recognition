#stackers.py

import numpy as np
from spkrec.db.neo4j.NeoCustomType import NeoCustomType

def stack_SVs(search_path, limit=None):
    """
    Reads SV data and returns multiples SV observations as rows
    """
    
    stacked_sv = np.array([])
    num_rec = len(search_path)
    num_iter = 0
    for sv_rec in search_path:
        
        num_iter = num_iter + 1
        if limit and num_iter > limit:
            break

        sv_data = NeoCustomType(sv_rec['sv'])
        reshape_size = np.max([np.size(sv_data,1), np.size(sv_data,0)])
        #print np.shape(sv_data), reshape_size
        sv_data = np.reshape(sv_data, (1,reshape_size))

        if not stacked_sv.any():
            stacked_sv = sv_data
        else:
            stacked_sv = np.vstack((stacked_sv, sv_data))
    
    return stacked_sv

def stack_SVs_random(db, speaker_name, limit):
    """
    Reads SV data and returns multiple SV observations as rows.  Random
    function reads from the 'random' key to pull up to "limit" number of
    random records from the collection.
    """

    #for i in range(limit):
    rand_num = np.random.ranf()

    sv_rec_cursor = db.get('sv', {'speaker_name': {'$ne': speaker_name}, 'random': {'$gte': rand_num}})
    #if not sv_rec_cursor:
    #    sv_rec_cursor = db.get('sv',{'speaker_name': {'$ne': speaker_name}, 'random': {'$lte': rand_num}}, random_pick=.10, limit=10)
    len_cursor = len(sv_rec_cursor)
    random_idx = [np.random.randint(0, len_cursor) for i in range(limit)]
    #print len_cursor
    #print random_idx
    idx = 0
    stacked_sv = np.array([])
    for sv_rec in sv_rec_cursor:
        if idx in random_idx:
            print sv_rec['speaker_name']
            sv_data = NeoCustomType(sv_rec['sv'])
            reshape_size = np.max([np.size(sv_data,1), np.size(sv_data,0)])

            sv_data = np.reshape(sv_data, (1,reshape_size))

            if not stacked_sv.any():
                stacked_sv = sv_data
            else:
                stacked_sv = np.vstack((stacked_sv, sv_data))
            if np.size(stacked_sv,0) == limit:
                break
        idx = idx + 1

    return stacked_sv

if __name__ == '__main__':
    from spkrec.db.neo4j import NeoEngine

    db = NeoEngine('/data/neo4j')

    for speaker in db.get('speaker'):
        print speaker['name']

        stacked = stack_SVs_random(db, speaker['name'], 10)
        print np.size(stacked,0)

    db.shutdown()
