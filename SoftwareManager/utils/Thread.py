'''
Created on 11 sept. 2016

@author: chakour
'''
import sys, subprocess
import threading

def popenAndCall(onExit, callbackOptions, command, shell, cwd):
    """
    Runs the given args in a subprocess.Popen, and then calls the function
    onExit when the subprocess completes.
    onExit is a callable object, and popenArgs is a list/tuple of args that 
    would give to subprocess.Popen.
    """
    def runInThread(onExit, callbackOptions, command, shell, cwd):
        print("Call command " + command)
        r = 0
        try :
            r = subprocess.check_output(command, shell=shell, cwd=cwd)
            onExit(callbackOptions, False)
        except subprocess.CalledProcessError as e:
            onExit(callbackOptions, e)
        return
    print("start thread")
    thread = threading.Thread(target=runInThread, args=(onExit, callbackOptions, command, shell, cwd))
    thread.start()
    # returns immediately after the thread starts
    return thread