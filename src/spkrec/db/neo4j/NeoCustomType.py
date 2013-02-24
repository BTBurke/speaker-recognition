# NeoCustomType.py
import numpy as np
import pickle
import json

from spkrec.db.riak import binary_store, binary_retrieve


class NeoCustomTypeError(Exception):
    pass

    

def NeoCustomType(value):
    if isinstance(value, str) or isinstance(value, unicode):
        value = json.loads(value)

    if isinstance(value, int):
        return value
    elif isinstance(value, float):
        return value
    elif isinstance(value, dict):
        # Logic if passed value has already been stored and must be retrieved
        # Returns regular dict type if not in correct NeoCustomType format
        if 'type' in value.keys() and value['type'] == 'NeoCustomType':
            action = 'retrieve'
        else:
            return json.dumps(value)

        if 'content_type' in value.keys():
            if value['content_type'] == 'numpy/ndarray':
                engine = _numpy_type
            else:
                raise NotImplementedError, "Custom type %s not implemented yet." % type(value)
    else:
        # Logic if passed value needs to be converted to binary and stored
        action = 'store'
        
        if isinstance(value, np.ndarray):
            engine = _numpy_type
        else:
            raise NotImplementedError, "Custom type %s not implemented" % type(value)
    
    retval = engine(value, action)
    return retval


def _numpy_type(value, action):
    
    if action == 'store':
        blob = pickle.dumps(value, 2)
        try:
            _id = binary_store(blob)
        except Exception:
            raise NeoCustomTypeError, "Failed on insert of binary blob."
        return json.dumps({'id': _id, 'type': 'NeoCustomType', 'content_type': 'numpy/ndarray'})

    if action == 'retrieve':
        try:
            data = binary_retrieve(str(value['id']))
        except Exception, e:
            print value['id']
            print type(value['id'])
            raise NeoCustomTypeError, 'Failed on retrieve of binary blob.'

        return pickle.loads(data)

if __name__ == '__main__':
    
    test = np.ones((1,15), dtype=np.float)

    id0 = NeoCustomType(test)
    print id0

    data = NeoCustomType(id0)
    print data
    
    test1 = {'name': 'Bryan', 'age': 36}
    id1 = NeoCustomType(test1)
    print id1
