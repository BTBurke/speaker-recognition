#test_mongoengine_ext.py

from spkrec.db.mongoengine_ext import SVMModelField, connect_to_database
from spkrec.db.schema import SVM
from scikits.learn.svm import SVC

def test_SVMModelField():
    X = [[0 ,0],[1, 1]]
    y = [0, 1]

    svm = SVM()
    clf = SVC()
    clf.fit(X,y)
    a1 = clf.predict([[2.,2.]])

    #print clf
    #print a1

    svm.classifier = clf
    svm.save(safe=True)

    s = SVM.objects.first()
    #print s.classifier
    a2 = s.classifier.predict([[2., 2.]])
    #print a2

    assert a1 == a2

if __name__ == '__main__':
    connect_to_database()
    test_SVMModelField()