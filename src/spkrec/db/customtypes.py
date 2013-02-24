import pymongo.binary
import snappy
from numpy import ndarray
from scikits.learn import svm
import pickle
from pymongo.son_manipulator import SONManipulator

class NumpyArrayField(object):
    """A Numpy array field with compression
       via Google's Snappy compression engine
    """
    def __init__(self, value):
        if isinstance(value, ndarray):
        	self._value = value
        else:
        	assert False, "Not a value numpy.ndarray type."

    def value(self):
    	return self._value

class SVMModelField(object):
    """A SVM object field with compression
       via Google's Snappy compression engine
    """
    def __init__(self, value):
        if isinstance(value, type(svm.SVC())) or isinstance(value, type(svm.LinearSVC())) or True:
        	self._value = value
        else:
        	assert False, "Not a value scikits.learn.SVM type."

    def value(self):
    	return self._value
 
def _enabled_types():
	"""
	Add custom types defined above to this return function
	to enable encode/decode functions below.
	"""
	return [SVMModelField, NumpyArrayField]

 ##########################################################
 # Implements encode/decode functions for custom types    #
 ##########################################################
    
class CustomReturnDict(object):
	"""
	Custom return dictionary automatically decodes custom types
	types to return native classes/types
	"""
	def __init__(self, value):
		self._value = value

	def __getitem__(self, key, *args, **kwargs):
		if [True for inst in _enabled_types() if isinstance(self._value[key], inst)]:
			return self._value[key].value()
		else:
			return self._value[key]
	def get(self, key, *args, **kwargs):
		return self.__getitem__(self, key)
    

class TransformToBinary(SONManipulator):
	"""
	Class to transform custom types to BSON and compress
	them on insert, and to convert back to custom types
	embedded in a CustomReturnDict class on retrieval
	"""

	def to_mongo(self,value):
		return pymongo.binary.Binary(snappy.compress(pickle.dumps(value, protocol=2)), 128)
	
	def to_python(self,value):
		return pickle.loads(snappy.uncompress(value))

	def transform_incoming(self, son, collection):
		for (key,value) in son.items():
			if [True for inst in _enabled_types() if isinstance(value, inst)]:
				son[key] = self.to_mongo(value)
			elif isinstance(value, dict):
				son[key] = self.transform_incoming(value, collection)
		return son

	def transform_outgoing(self, son, collection):
		for (key, value) in son.items():
			if isinstance(value, pymongo.binary.Binary) and value.subtype == 128:
				son[key] = self.to_python(value)
			elif isinstance(value, dict):
				son[key] = self.transform_outgoing(value, collection)
		#return CustomReturnDict(son)
		return son

if __name__ == '__main__':
	from spkrec.db.mongoengine_ext import connect_to_database
	import numpy as np

	db = connect_to_database('test', True)
	db.add_son_manipulator(TransformToBinary())
	
	#Test SVM model storage and retrieval
	X = np.array([[-1, -1], [-2, -1], [1, 1], [2, 1]])
	y = np.array([1, 1, 2, 2])
	clf = svm.SVC()
	clf.fit(X,y)
	id = db.test.insert({'test': SVMModelField(clf), 'test2': 5})
	val = db.test.find_one({'_id': id})
	print val['test'], val['test2']

	#Test Numpy array storage and retrieval
	a = np.ones((1,5))
	id = db.test.insert({'test': NumpyArrayField(a), 'test2': 5})
	val = db.test.find_one({'_id': id})
	print val['test'], val['test2']