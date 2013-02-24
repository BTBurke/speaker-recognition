import riak
import uuid
import pickle

def binary_store(blob, collection='spkrec'):
    bucket = _riak_connect(collection)  
    _id = str(uuid.uuid4().hex)
    rec = bucket.new_binary(_id, data=blob)
    rec.store()		
    return _id

def binary_retrieve(_id, collection='spkrec'):
    bucket = _riak_connect(collection)	
    rec = bucket.get_binary(_id)
    return rec.get_data()

def _riak_connect(collection, _port=8087, _transport_class=riak.RiakPbcTransport):
    
    try:
        db = riak.RiakClient(port=_port, transport_class=_transport_class)
        bucket = db.bucket(collection)
    except Error, e:
        raise e, "Failed to connect to Riak"

    return bucket

if __name__ == '__main__':
    import numpy as np

    test = {'name': 'Bryan', 'age': 36}
    test1 = np.ones((1,12), dtype=np.float)

    id0 = binary_store(pickle.dumps(test,2))
    print pickle.loads(binary_retrieve(id0))

    id1 = binary_store(pickle.dumps(test1, 2))
    print pickle.loads(binary_retrieve(id1))

