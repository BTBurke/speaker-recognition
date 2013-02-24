
from neo4j import GraphDatabase, OUTGOING, INCOMING, Evaluation
import uuid
import random
from spkrec.db.neo4j.NeoCustomType import NeoCustomTypeError, NeoCustomType

class NeoEngineError(Exception):
    pass
class NeoEngine():

    def __init__(self, db_path):
        db = self.connect_to_neo4j(db_path)
        self.db = db
        
    def connect_to_neo4j(self, db_path):

        try:
            db = GraphDatabase(db_path)
        except Exception, e:
            print "%s: Could not connect to database." % e
        
        return db

    def get_collections(self):
        
        if not self.db:
            raise NeoEngineError, "No database connection."

        db = self.db

        collections = {}
        for relationship in db.reference_node.COLLECTION:
            head = relationship.end
            if head.has_key('type') and head['type'] == 'collection_head':
                collections[head['name']] = head

        return collections

    def create_collection(self, collection_name):
        
        db = self.db
        existing_collections = self.get_collections()

        if collection_name in existing_collections:
            db.shutdown()
            raise NeoEngineError, '%s collection already exists' % collection_name
        _id = str(uuid.uuid4().hex)
        
        with db.transaction:
            head = db.node(name = collection_name, 
                            type='collection_head',
                            id = _id)
            db.reference_node.COLLECTION(head)
            idx = db.node.indexes.create(collection_name)
        return _id
    
    def delete_collection(self, collection_name):
        db = self.db
        with db.transaction:
            for node in self.get(collection_name):
                self.delete_node(node)
        with db.transaction:
            collections = self.get_collections()
            self.delete_node(collections[collection_name])


    def delete_node(self, node):
        db = self.db
        with db.transaction:
            for rel in node.relationships:
                rel.delete()
            node.delete()
        
    def create_index(self, collection_name, key):
        db = self.db
        with db.transaction:
            idx = db.node.indexes.get(collection_name)
            nodes = self.get(collection_name)
            for node in nodes:
                try:
                    idx[key][node[key]] = node
                except Exception, e:
                    print 'Warning: %s' % e
                    for key, value in node.items():
                        print '%s: %s' % (key, value)

    def get_index(self, collection_name):

        db = self.db
        with db.transaction:
            return db.node.indexes.get(collection_name)
    
    def get_properties_as_dict(self, node_or_rel):
        return dict([(k,v) for k,v in node_or_rel.items()])

    def insert(self, collection, properties):
        db = self.db

        cols = self.get_collections()
        idx = self.get_index(collection)

        # If ID already exists, assume update 
        if 'id' in properties.keys():
            node = db.get(collection, {'id': properties['id']})
            with db.transaction:
                for key, value in properties.items():
                    if isinstance(value, str):
                        node[key] = value
                    else:
                        try:
                            node[key] = NeoCustomType(value)
                        except NeoCustomTypeError:
                            db.shutdown()
                            raise NeoEngineError, "Error inserting custom type: %s" % type(value)
            return node

        # Otherwise insert new node and connect to colleciton head
        with db.transaction:
            node = db.node()
            for key, value in properties.items():
                if isinstance(value, str):
                    node[key] = value
                else:
                    try:
                        node[key] = NeoCustomType(value)
                    except NeoCustomTypeError:
                        db.shutdown()
                        raise NeoEngineError, "Error inserting custom type: %s" % type(value)

            node['id'] = str(uuid.uuid4().hex)
            node.INSTANCE_OF(cols[collection])
            idx['id'][node['id']] = node
        return node
            
    def get(self, collection, search_params={}, single=False, random_pick=False, limit=False):

        ret_num = 0

        db = self.db

        #First see if any search parameter is indexed
        # TODO: Only allows single valued indexes, compound indexes would be fast but hard?
        try:
            idx = self.get_index(collection)
        except Exception:
            idx = None
        if idx:
            if 'id' in search_params:
                return idx['id'][search_params['id']].single
            if len(search_params.keys()) == 1:
                for key in search_params.keys():
                    if not isinstance(search_params[key], dict):
                        hits = idx[key][search_params[key]]
                        if len(hits) > 0:
                            return idx[key][search_params[key]]

        #Without search params, return whole collection
        #as iterable
        collections = self.get_collections()
        start_node = collections[collection]

        def _eval_no_head(path):
            if path.end.has_key('type') and path.end['type'] == 'collection_head':
                return Evaluation.EXCLUDE_AND_CONTINUE
            else:
                return Evaluation.INCLUDE_AND_CONTINUE

        if not search_params:
            traverser = db.traversal().evaluator(_eval_no_head).relationships('INSTANCE_OF', INCOMING).traverse(start_node)
            return traverser.nodes

        #With search params, evaluate path and return
        #matching records
        def _complex_op(actual, test, op):
            if op == '$ne':
                if actual != test:
                    return True
                else:
                    return False
            elif op == '$gt':
                if actual > test:
                    return True
                else:
                    return False
            elif op == '$lt':
                if actual < test:
                    return Truse
                else:
                    return False
            elif op == '$gte':
                if actual >= test:
                    return True
                else:
                    return False
            elif op == '$lte':
                if actual <= test:
                    return True
                else:
                    return False
            else:
                raise NotImplementedError, "Complex operator %s not implemented" % op

        def _eval_search_params(path):
            if path.end.has_key('type') and path.end['type'] == 'collection_head':
                return Evaluation.EXCLUDE_AND_CONTINUE
            else:
                for key, value in search_params.items():
                    if type(value) == dict:
                        for op, test in value.items():
                            if path.end.has_key(key) and _complex_op(path.end[key], test, op):
                                pass
                            else:
                                return Evaluation.EXCLUDE_AND_CONTINUE
                    else:
                        if path.end.has_key(key) and path.end[key] == value:
                            pass
                        else:
                            return Evaluation.EXCLUDE_AND_CONTINUE
                return Evaluation.INCLUDE_AND_CONTINUE
                
                if random_pick:
                    ranf = random.random()
                    print "Doing Random Pick"
                    print ranf
                    print ret_num
                    if ranf < random_pick:
                        # It is a random pick, if it's a single, return and stop
                        # if it's limited, return and continue < limit
                        if single:
                            "doing random single"
                            return Evaluation.INCLUDE_AND_PRUNE
                        elif limit:
                            "doing random limit"
                            if ret_num == limit:
                                "Random end limit"
                                return Evaluation.INCLUDE_AND_PRUNE
                            else:
                                "Random less than limit"
                                ret_num = ret_num + 1
                                return Evaluation.INCLUDE_AND_CONTINUE
                        else:
                            "Random regular"
                            return Evaluation.INCLUDE_AND_CONTINUE
                    else:
                        "Not a randome pick"
                       # Not a random pick, keep going
                        return Evaluation.EXCLUDE_AND_CONTINUE
                elif single:
                    print "Doing Single"
                    return Evaluation.INCLUDE_AND_PRUNE
                elif limit:
                    print "Doing limit without random"
                    if ret_num == limit:
                        return Evaluation.INCLUDE_AND_PRUNE
                    else:
                        ret_num = ret_num + 1
                        return Evaluation.INCLUDE_AND_CONTINUE
                else:
                    print "Doing straight stick"
                    return Evalution.INCLUDE_AND_CONTINUE
                
        traverser = db.traversal().evaluator(_eval_search_params).relationships('INSTANCE_OF', INCOMING).traverse(start_node)
        #print ret_num
        return traverser.nodes	

    def shutdown(self):
        self.db.shutdown()


if __name__ == '__main__':
    import random
    from clint.textui.progress import bar
    import numpy as np

    db = NeoEngine('/home/ubuntu/test')

    for col in ['speaker', 'mfcc']:
        db.create_collection(col)
    for i in bar(range(200)):

        props = {'name': 'Bryan', 'age': random.randint(2,100)}
        node = db.insert('speaker', props)
    
    node2 = db.get('speaker')
    print "%i should be 200" % len(node2)

    node2 = db.get('speaker', {'name': 'Bryan'})
    print "%i should be 200" % len(node2)

    node2 = db.get('speaker', {'age': {'$gt': 95}})
    for node in node2:
        for key, value in node.items():
            print '%s: %s' % (key, value)

    db.delete_collection('speaker')
    print db.get_collections()

    db.shutdown()
