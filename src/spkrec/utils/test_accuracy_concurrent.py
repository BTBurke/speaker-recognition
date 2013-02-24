#test_accuracy_concurrent.py

from spkrec.db.schema import *
from spkrec.db.mongoengine_ext import connect_to_database
from spkrec.algorithm.concurrent_cursor import *
from spkrec.algorithm.svm import train_svm_crossvalidated, test_svm_accuracy
from scikits.learn.cross_val import StratifiedKFold

from celery.task import task
import numpy as np
from clint.textui.progress import bar
from spkrec.db.customtypes import *
from multiprocessing import Process
import zmq

#for testing
import csv

@task
def test_accuracy_concurrent(worker, concurrency):
    TEST_FOLD = 2
    RUN_MAX = False
    iter_num = 0
    db = connect_to_database()
    db.add_son_manipulator(TransformToBinary())
    

    #take this out later when testing complete
    fid = open('/home/ubuntu/project/backend-search/src/spkrec/utils/hist'+str(worker)+'.csv', 'wb')
    csv_writer = csv.writer(fid)
    if worker == 0:
        csv_writer.writerow(['name', 'num speaker SVs', 'test subjects', 'test impostors', 'correct subject', 'correct impostor', 'false neg', 'false pos'])

    cursor = Concurrent_cursor(Speaker.objects())
    cursor.set_concurrency(concurrency)
    cursor.set_worker(worker)


    for speaker in Speaker.objects():
        #Impostor ratio is ratio of impostor records in training
        #and testing population.  For ratio=N, subject is 1/(N+1),
        #impostor N/(N+1) of population
        IMPOSTOR_RATIO = 3

        #Find all SVs for current subject
        print 'Speaker Name: %s' % speaker.name
        #print 'Count:', db.sv.find({'speaker_name': speaker.name}).count()
        #cursor_subject = Concurrent_cursor(SV.objects(speaker_name=speaker.name))
        sv_subject = stack_SVs(db.sv.find({'speaker_name': speaker.name}))
        num_subject = np.size(sv_subject,0)
        
        #csv_writer.writerow([speaker.name, num_subject])
        #print num_subject
        if num_subject < 20:
            continue
        
        #Get random SVs from rest of database for test population
        #cursor_impostor = db.sv.find({'speaker_name': {'$ne': speaker['name']}})
        sv_impostor = stack_SVs_random(db, speaker.name, num_subject*IMPOSTOR_RATIO)
        num_impostor = np.size(sv_impostor,0)
        print 'Subject: %i, Impostor: %i' % (num_subject, num_impostor)

        #generate total dataset of observations X with class labels y
        X = np.vstack((sv_subject, sv_impostor))
        y = np.array([1] * num_subject + [0] * num_impostor)

        #Pick random assortment from each set to form training observations
        #Switch ensures that smaller number always used for training
        if TEST_FOLD < 3:
            train, test = iter(StratifiedKFold(y, TEST_FOLD)).next()
        else:
            test, train = iter(StratifiedKFold(y, TEST_FOLD)).next()
        #print train

        #Perform crossvalidated SVM training
        #print type(X), type(y)
        #print np.shape(X[train]), np.shape(y[train])

        clf = train_svm_crossvalidated(X[train], y[train])
        #print type(clf)

        #clf_rec = {'classifier': SVMModelField(clf), 'speaker_name': speaker.name}
        #db.svm.insert(clf_rec, safe=True)

        #Collect classification statistics
        accuracy = test_svm_accuracy(X[test], y[test], clf)
        num_subject_test = np.sum(y[test])
        num_impostor_test = len(y[test]) - num_subject_test
        print 'Accuracy: %f' % (float(accuracy['correct_subject'])/float(num_subject_test))
        print 'Sub: %i/%i  Imp: %i/%i' % (accuracy['correct_subject'], num_subject_test, accuracy['correct_impostor'], num_impostor_test)
        print 'False Neg: %i  False Pos: %i' % (accuracy['false_neg'], accuracy['false_pos'])

        csv_writer.writerow([speaker.name, num_subject, num_subject_test, num_impostor_test, accuracy['correct_subject'], accuracy['correct_impostor'], accuracy['false_neg'], accuracy['false_pos']])
        iter_num = iter_num + 1

        #if RUN_MAX and iter_num >= RUN_MAX:
        #    print "I'm breaking"
        #    break
        #print num_subject, num_impostor
    fid.close()
    print "Complete"

def stack_SVs(search_path):
    """
    Reads SV data and returns multiples SV observations as rows
    """
    
    stacked_sv = np.array([])
    for sv_rec in search_path:
        
        sv_data = sv_rec['sv'].value()
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

    for i in range(limit):
        rand_num = np.random.ranf()

        sv_rec_cursor = db.sv.find({'speaker_name': {'$ne': speaker_name}, 'random': {'$gte': rand_num}}).limit(1)
        if not sv_rec_cursor:
            sv_rec_cursor = db.sv.find({'speaker_name': {'$ne': speaker_name}, 'random': {'$lte': rand_num}}).limit(1)

        for sv_rec in sv_rec_cursor:
            sv_data = sv_rec['sv'].value()
            reshape_size = np.max([np.size(sv_data,1), np.size(sv_data,0)])

            sv_data = np.reshape(sv_data, (1,reshape_size))

            if i == 0:
                stacked_sv = sv_data
            else:
                stacked_sv = np.vstack((stacked_sv, sv_data))
        
    return stacked_sv
