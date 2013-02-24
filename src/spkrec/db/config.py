#!/usr/bin/env python
#config.py
#
# Writes text config files from configuration information stored in DB
#
# Copyright Xemplar Biometrics, 2011


def write_config(config, filename, dir='/tmp/'):
    
    with open(dir+filename, 'w') as fid:
        for key in config.keys():
            fid.write(key + ' ' + config[key] + '\n')
    fid.close()
    
    return dir+filename

def read_config(filename):
    
    config = {}
    with open(filename, 'r') as fid:
        for line in fid.readlines():
            line_split = line.split(' ')
            config[line_split[0]] = line_split[1].rstrip()
    fid.close()
    
    return config

if __name__ == '__main__':
    
    a = {'test1': 'test2', 'test3': 'test4'}  
    fname = write_config(a, 'test.config')   
    b = read_config(fname)
    
    assert a==b
    
