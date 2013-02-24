#add_random_queryfield.py

from spkrec.db.schema import *
from spkrec.db.mongoengine_ext import connect_to_database
from clint.textui.progress import bar
import numpy as np

def add_random_queryfield(collection):

    c = connect_to_database()

    for rec in bar(collection.objects()):
        rec.random = np.random.ranf()
        rec.save(safe=True)
    
    collection.objects.ensure_index('random')


if __name__ == '__main__':
    add_random_queryfield(SV)