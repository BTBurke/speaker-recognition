#test_accuracy.py

from celery.task import task
from spkrec.utils.test_accuracy_concurrent import test_accuracy_concurrent

def test_accuracy(concurrency):
    for i in range(concurrency):
        test_accuracy_concurrent.delay(i, concurrency)


if __name__ == '__main__':

    test_accuracy(1)

