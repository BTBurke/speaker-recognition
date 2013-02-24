#svm.py

import numpy as np
from scikits.learn.svm import SVC, LinearSVC
from scikits.learn.grid_search import GridSearchCV
from scikits.learn.cross_val import StratifiedKFold
from scikits.learn.metrics import recall_score

from pprint import pprint

def train_svm_crossvalidated(X, y, tuned_parameters={'kernel': ['rbf'], 'gamma': 2.0**np.arange(-15,3), 'C': 2.0**np.arange(-5, 15)}):
    """
    Performs grid search with stratified K-fold cross validation on observations X with 
    true labels y and returns an optimal SVM, clf
    """

    k_fold = _size_dependent_k_split(np.size(X,0))

    clf = GridSearchCV(SVC(C=1), tuned_parameters, score_func=recall_score)
    clf.fit(X, y, cv=StratifiedKFold(y, k_fold))

    y_true, y_pred = y, clf.predict(X)

    #print "Classification report for the best estimator: "
    #print clf.best_estimator
    print "Tuned with optimal value: %0.3f" % recall_score(y_true, y_pred)
    
    return clf

def _size_dependent_k_split(num_obs):
    """
    Returns split for stratified K-fold depending on the number of available observations
    """
    if num_obs < 5:
        print "WARNING: Very small number of observations for SVM training"
        return 1
    elif num_obs < 10:
        return 2
    elif num_obs < 30:
        return 3
    else:
        return 5

def test_svm_accuracy(X, y, clf):
    """
    Given a test set of observations X and true class labels y with SVM clf, return
    dictionary of correct classifications, false negatives, and false positives
    """

    y_correct_sub, y_correct_imp, y_false_neg, y_false_pos = _inspect_accuracy(y, clf.predict(X))

    return {'correct_subject': y_correct_sub, 'correct_impostor': y_correct_imp, 'false_neg': y_false_neg, 'false_pos': y_false_pos}


def _inspect_accuracy(y_true, y_pred):
    """
    Returns number of predicted classes correct, false positives, and false negatives
    """   
    y_correct_sub = 0
    y_correct_imp = 0
    y_false_neg = 0
    y_false_pos = 0

    for y_t, y_p in zip(y_true,y_pred):
        if y_t == y_p:
            if y_t:
                y_correct_sub = y_correct_sub + 1
            else:
                y_correct_imp = y_correct_imp + 1
        elif y_t > y_p:
            y_false_neg = y_false_neg + 1
        else:
            y_false_pos = y_false_pos + 1
    
    return y_correct_sub, y_correct_imp, y_false_neg, y_false_pos

              
        

