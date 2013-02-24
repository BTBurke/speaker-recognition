#map_adapt_concurrent.py

from spkrec.db.schema import *
from spkrec.db.mongoengine_ext import connect_to_database
from spkrec.algorithm.concurrent_cursor import *
from spkrec.algorithm.energydetector import strip_silence
from spkrec.algorithm.map_adapt import map_adapt_speaker, convert_type_db_gmm
from spkrec.algorithm.supervector import create_supervector
from spkrec.db.customtypes import *
from scikits.learn import mixture
from celery.task import task
import numpy as np
from clint.textui.progress import bar

@task
def map_adapt_concurrent(t, world, worker, concurrency):
    db = connect_to_database()
    db.add_son_manipulator(TransformToBinary())

    cursor = Concurrent_cursor(Mfcc.objects(__raw__={'speaker_name': {'$ne': 'anonymous'}}))
    cursor.set_concurrency(concurrency)

    #print "eat it bitch"
   
    #print cursor.concurrency
    silent_records = 0
    cursor.set_worker(worker)
    #print cursor.worker

    for mfcc in bar(cursor.search_path()):

        mfcc_speech = strip_silence(mfcc.data, mfcc.energydetectorindex)
            
        # Check for silent recordings and skip if found
        if not mfcc_speech.any():
            silent_records = silent_records + 1
            continue

        #Compute number of full windows of len t
        ind = np.arange(0, np.size(mfcc_speech,0), t/.01)
        if len(ind) > 1:
            for i in range(len(ind)-1):
                obs = mfcc_speech[ind[i]:ind[i+1],:]
                model_w, model_u = map_adapt_speaker(obs, world)
                
                model_rec = {'base_ubm': mfcc.id, 
                            'speaker_name': mfcc.speaker_name,
                            'speaker': mfcc.speaker, 
                            'train_time': t,
                            'model_weights': NumpyArrayField(np.reshape(model_w, (np.size(model_w,0),1))),
                            'model_means': NumpyArrayField(model_u)}
                
                db.model.insert(model_rec, safe=True)
                #m = Model()
                #m.base_ubm = mfcc.id
                #m.speaker_name = mfcc.speaker_name
                #m.speaker = mfcc.speaker
                #m.train_time = t
                #m.model_weights = np.reshape(model_w, (np.size(model_w,0),1))
                #m.model_means = model_u
                #m.save(validate=False)
    print "Number of silent records: %s" % str(silent_records)

@task
def create_SV_from_GMM(worker, concurrency):
    db = connect_to_database()
    #print db
    db.add_son_manipulator(TransformToBinary())

    #print db.collection_names()
    model = db['spkrec']
    #print model
    #total_cnt = db.model.count()
    #total_cnt = model.count()
    #print total_cnt
    
    cursor = Concurrent_cursor(db.model.find())
    cursor.set_concurrency(concurrency)
    cursor.set_worker(worker)
    total_cnt = cursor.search_path().count()
    #print cursor.cursor

    u = Ubm.objects.first()
    #print np.shape(u.ubm_weights)
    #print np.shape(u.ubm_means)
    #print np.shape(u.ubm_vars)

    bar_iter = bar([i for i in range(total_cnt)])
    for model in cursor.search_path():
        bar_iter.next()
        #print iter_num
        #print np.shape(model.model_means)
        sv_data = create_supervector(u.ubm_weights, model['model_means'].value(), u.ubm_vars)
        #print np.shape(sv_data)

        sv_rec = {'base_model': model['_id'], 
                'sv': NumpyArrayField(sv_data), 
                'speaker_name': model['speaker_name'],
                'speaker': model['speaker'], 
                'random': np.random.ranf()}
        
        db.sv.insert(sv_rec, safe=True)
        #sv_init = SV()
        #sv_init.base_model = model.id
        #sv_init.sv = sv_data
        #sv_init.speaker_name = model.speaker_name
        #sv_init.speaker = model.speaker
        #sv_init.random = np.random.ranf()
        #sv_init.save(safe=True)

