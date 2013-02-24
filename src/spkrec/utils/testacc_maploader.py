#testacc_maploader.py

import time

def setup():
    x = '1'
    y = '2'
    return [x, y]

if __name__ == '__main__':
    a = setup()
    print a
    time.sleep(60)
    print 'Finished'