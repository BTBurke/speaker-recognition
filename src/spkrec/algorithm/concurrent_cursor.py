#search_strategy.py
#
# Copyright 2011, Xemplar Biometrics Inc.

import numpy as np

class ConcurrentCursorError(Exception):
    pass

class Concurrent_cursor():
 

    def __init__(self, cursor, strategy = 'linear'):
        """
        Defaults to searching the entire database.
        self.set_concurrency(workers) configures the cursor for multiple workers
        self.search_path() returns an iterable cursor
        """
        if strategy == 'linear':
            self.search_path = self.path_linear
            self.strategy = 'linear'
        elif strategy == 'random':
            self.strategy = 'random'
            self.search_path = self.path_random
        else:
            assert False, "Not a valid search strategy."
        
        self.worker = 0
        self.concurrency = 1
        self.cursor = cursor
    
    # Implements special methods for pickling class 
    # from http://docs.python.org/release/3.0.1/library/pickle.html#pickle-state
    def __getstate__(self):
        state = self.__dict__.copy()
        del state['search_path']
        return state

    def __setstate__(self,state):
        self.__dict__.update(state)
        if self.strategy == 'linear':
            self.search_path = self.path_linear
        elif self.strategy == 'random':
            self.search_path = self.path_random
        else:
            assert False, "Failed to restore strategy from pickle."

    
    def set_concurrency(self, workers):
        """
        Sets concurrency
        """
        self.concurrency = workers
    
    def set_worker(self, worker_id):
        """
        Set worker id prior to search_path call if retry
        """
        self.worker = worker_id
    
    def path_linear(self):
        """
        Returns a cursor to a subset of the database based on the total number
        or workers configured
        """

        if self.worker >= self.concurrency:
            raise ConcurrentCursorError("More tasks were spawned than configured workers.")
        #if self.worker == 0:
        self.total_cnt = self.cursor.count()
        self.index = np.floor(np.linspace(0,self.total_cnt,self.concurrency+1))

        return_cursor = self.cursor[self.index[self.worker]:self.index[self.worker+1]]
        #self.worker = self.worker + 1

        return return_cursor
    
    def path_random(self, limit=False):
        """
        Returns a cursor with random permutation.  Limited to limit if provided.
        """
        if self.worker >= self.concurrency:
            raise ConcurrentCursorError("More tasks were spawned than configured workers.")
        if self.worker == 0:
            self.total_cnt = self.cursor.count()
            self.randpath = np.random.permutation(range(self.total_cnt))
            if limit:
                if limit < self.total_cnt:
                    self.randpath = self.randpath[0:limit]
            self.index = np.floor(np.linspace(0,len(self.randpath),self.concurrency+1))
        
        print list(np.sort(self.randpath[self.index[self.worker]:self.index[self.worker+1]]))

        #return_cursor = [self.cursor[ind] for ind in np.sort(self.randpath[self.index[self.worker]:self.index[self.worker+1]])]
        return_cursor = self.cursor([ind for ind in np.sort(self.randpath[self.index[self.worker]:self.index[self.worker+1]])])
        #self.worker = self.worker + 1

        return return_cursor

