# processrunner.py
# Reads from YAML file and spawn processes or threads given the config file parameters
#
# Copyright 2011, Xemplar Biometrics, Inc

import yaml
import subprocess
import sys
import os
import time

class ProcessRunnerException(Exception):
    pass

class ProcessRunner():
    
    def __init__(self, yaml_file):

        #Dictionary to store various state values
        self.setup_values = {}
        self.pid = {}

        with open(yaml_file) as yfile:
            
            self.yaml = {}
            
            for p in yaml.load_all(yfile):
                self.yaml[p['Type']] = p
                self._parse_and_run(p)
        
        self._monitor()

    def _parse_and_run(self, p):
        """
        Parses an input YAML file and sets up various options:

        Global:
            Required:
                Type:           global-variables
                Base_dir:       Head of python import path for project
            Optional:
                Logfile:        Name of log file
        
        Process:
            Required:
                Type:           Human readable description of process type
                Source:         Source file to run in Python import format (org.xemplar.process)
                Number:         Number or processes to spawn
            Optional:
                Logging:        True/False
                Call_Setup:     True/False.  Calls setup() method within source file.
                Setup_Returns:  Names of variables returned in a list from setup() ['a', 'b']
                Arguments:      List of strings for command line arguments.  Setup_Returns variables
                                are substituted with values returned by setup().
                On_Failure:     Restart - Restarts the process by rereading from the YAML config
                                Killall - Fatal error that kills all running processes
        """

        if 'Base_dir' in p.keys():
            self.base = p['Base_dir']

        if 'Logging' in p.keys() and p['Logging']:
            print ("Should be setting up logfile")
        
        if 'Call_Setup' in p.keys() and p['Call_Setup']:
            mod = __import__(p['Source'], fromlist=['setup'])
            retval = mod.setup()
            self.setup_values.update(dict(zip(p['Setup_Returns'], retval)))
        
        #Launch processes
        if 'Number' in p.keys():
            for proc in range(p['Number']):

                #Process argument list
                if 'Arguments' in p.keys():
                    for idx, arg in enumerate(p['Arguments']):
                        # Replace arguments from call to setup with returned values
                        if arg in self.setup_values.keys():
                            p['Arguments'][idx] = self.setup_values[arg]
                
                #create command line with optional arguments
                if not self.base:
                    raise ProcessRunnerException, 'Base directory not set.  Set Base_dir in YAML file.'
                
                prog_cmd = self.base + '/'.join(p['Source'].split('.')) + '.py'

                if not os.path.exists(prog_cmd):
                    raise ProcessRunnerException, 'Source file %s does not exist in this path.' % p['Source']

                arglist = ['python', prog_cmd]

                if 'Arguments' in p.keys():
                    for L in p['Arguments']:
                        arglist.append(L)
                
                # Launch processes
                pid = subprocess.Popen(arglist)
                
                #Register PIDs in state dict as list of Popen classes enabling further process interaction
                if p['Type'] in self.pid.keys():
                    self.pid[p['Type']].append(pid)
                else:
                    self.pid[p['Type']] = [pid]

    def _monitor(self, sleep_time=5):
        """
        Loop and check status.  None indicates process running, 0 indicates success.
        Processes are removed as they terminate naturally or passed to _handle_failure.
        Periodicity defaults to 5 seconds to prevent running CPU to 100.
        """

        while self.pid.keys():
            for key in self.pid.keys():
                for idx, pid in enumerate(self.pid[key]):
                    
                    status = pid.poll()
                    
                    if status is not None and status is not 0:
                        print "WARNING: Process %i Terminated Unexpectedly" % pid.pid
                        self.pid[key].pop(idx)
                        self._handle_failure(key, pid)

                    elif status is 0:
                        self.pid[key].pop(idx)
                        if len(self.pid[key]) == 0:
                            del self.pid[key]
            time.sleep(sleep_time)


    def _handle_failure(self, process_type, popen_class):
        """
        Checks reason for process failure.  If not terminated by the user, it reads
        On_Failure from YAML config and takes action to restart process or kill 
        whole job
        """

        kill_reason = popen_class.poll()
        if kill_reason == -9 or kill_reason == -15:
            print "%s: PID %i: Killed by user, will not restart." % (process_type, popen_class.pid)
        
        p = self.yaml[process_type]

        if 'On_Failure' in p.keys():

            if p['On_Failure'] == 'Restart':
                print "%s: PID %i: Process died.  Restarting." % (process_type, popen_class.pid)
                p_altered = p
                p_altered['Number'] = 1
                self._parse_and_run(p_altered)
            
            if p['On_Failure'] == 'Killall':
                print "%s: PID %i: Process died.  Killing job." % (process_type, popen_class.pid)
                for key in self.pid.keys():
                    for pid in self.pid[key]:
                        pid.kill()
                self.pid = {}
                    

if __name__ == '__main__':

    import argparse

    parser = argparse.ArgumentParser(description = "Reads from a YAML config file and runs a processing workflow.")
    parser.add_argument('yaml_file', nargs='+')
    c = parser.parse_args()

    for yaml_file in c.yaml_file:
        ProcessRunner(yaml_file)
