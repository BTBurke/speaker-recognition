from spkrec.db.schema import *
from spkrec.db.mongoengine_ext import connect_to_database
from spkrec.algorithm.concurrent_cursor import *
from spkrec.algorithm.svm import train_svm_crossvalidated, test_svm_accuracy
from scikits.learn.cross_val import StratifiedKFold
from spkrec.db.neo4j import NeoEngine

#from celery.task import task
import numpy as np
from clint.textui.progress import bar
from spkrec.db.customtypes import *
from multiprocessing import Process
import zmq
from spkrec.utils.stackers import stack_SVs, stack_SVs_random
from clint.textui.progress import bar

#for testing
import csv
import time
import uuid
import random

def mapper(db):
    #db = connect_to_database()
    #db.add_son_manipulator(TransformToBinary())
    #db = NeoEngine('/data/neo4j')

    ctx = zmq.Context()
    q = ctx.socket(zmq.PUSH)
    q.bind("tcp://127.0.0.1:5555")
    time.sleep(3)

    for speaker in db.get('speaker'):
        #print 'Sending %s' % speaker['name']
        q.send_json(speaker['name'])

    

def process_speaker(db):
    TEST_FOLD = 2
    #db = connect_to_database()
    #db.add_son_manipulator(TransformToBinary())
    #db = NeoEngine('/data/neo4j')

    #Impostor ratio is ratio of impostor records in training
    #and testing population.  For ratio=N, subject is 1/(N+1),
    #impostor N/(N+1) of population
    IMPOSTOR_RATIO = 3
    LIMIT = 30

    #Set up queue
    ctx = zmq.Context()
    q = ctx.socket(zmq.PULL)
    q.connect("tcp://127.0.0.1:5555")
    outQ = ctx.socket(zmq.PUSH)
    outQ.connect("tcp://127.0.0.1:5556")

    while True:
        speaker_name = q.recv_json()
        print 'Received %s' % speaker_name

        #time.sleep(random.randint(1,10))
        #Find all SVs for current subject
        #print 'Speaker Name: %s' % speaker.name
        #print 'Count:', db.sv.find({'speaker_name': speaker.name}).count()
        #cursor_subject = Concurrent_cursor(SV.objects(speaker_name=speaker.name))
        sv_subject = stack_SVs(db.get('sv', {'speaker_name': speaker_name}),limit=LIMIT)
        num_subject = np.size(sv_subject,0)
        print num_subject
        if num_subject < 20:
            continue
        
        #Get random SVs from rest of database for test population
        #cursor_impostor = db.sv.find({'speaker_name': {'$ne': speaker['name']}})
        sv_impostor = stack_SVs_random(db, speaker_name, num_subject*IMPOSTOR_RATIO)
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
        #print 'Sub: %i/%i  Imp: %i/%i' % (accuracy['correct_subject'], num_subject_test, accuracy['correct_impostor'], num_impostor_test)
        #print 'False Neg: %i  False Pos: %i' % (accuracy['false_neg'], accuracy['false_pos'])
        msg = {'speaker_name': speaker_name, 'accuracy': accuracy, 'num_subject': num_subject, 'num_subject_test': num_subject_test, 'num_impostor_test': num_impostor_test} 
        outQ.send_pyobj(msg)


def reducer():

    ctx = zmq.Context()
    inQ = ctx.socket(zmq.PULL)
    inQ.bind('tcp://127.0.0.1:5556')
    time.sleep(1)

    fname = str(uuid.uuid1())
    fid = open('/home/ubuntu/project/backend-search/src/spkrec/utils/'+fname+'.csv', 'wb')
    csv_writer = csv.writer(fid)
    csv_writer.writerow(['name', 'num speaker SVs', 'test subjects', 'test impostors', 'correct subject', 'correct impostor', 'false neg', 'false pos'])
    fid.close()

    while True:
        msg = inQ.recv_pyobj()
        accuracy = msg['accuracy']
        num_subject = msg['num_subject']
        num_subject_test = msg['num_subject_test']
        num_impostor_test = msg['num_impostor_test']
        speaker_name = msg['speaker_name']
    
        fid = open('/home/ubuntu/project/backend-search/src/spkrec/utils/'+fname+'.csv', 'ab')
        csv_writer = csv.writer(fid)

        csv_writer.writerow([speaker_name, num_subject, num_subject_test, num_impostor_test, accuracy['correct_subject'], accuracy['correct_impostor'], accuracy['false_neg'], accuracy['false_pos']])

        fid.close()


if __name__ == '__main__':
    CONCURRENCY = 1
    
    db = NeoEngine('/data/neo4j')
    
    for worker in range(CONCURRENCY):
        #time.sleep(random.randint(1,10))
        Process(target=process_speaker, args=(db,)).start()

    Process(target=reducer).start()
    Process(target=mapper, args=(db,)).start()
    
