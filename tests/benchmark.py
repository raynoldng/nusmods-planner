import unittest
import sys
sys.path.append('../nusmodsplanner')
from querySolver import *
import mod_utils
from stopwatch import *

def benchmark(f):
    """Convenience method to time execution of function and prints out time

    :param f: function to run
    :returns: 
    :rtype: 

    """
    t = Timer()
    t.start()
    f()
    print t.stop() + ' s'

def run1():
    s = timetablePlanner(5, ['cs1010', 'st2131', 'cs1231', 'ma1101r','cs2020','cs1020','cs2010'])
    for i in s:
        print i
    print mod_utils.gotFreeDay(s)

def run2():
    s = timetablePlannerv3(4, [], ['cs1010', 'st2131', 'cs1231', 'ma1101r','cs2020',
                                   'cs2010', 'ma2108'])

def run3():
    s = minTravelQueryv3(4, [], ['cs1010', 'st2131', 'cs1231', 'ma1101r','cs2020',
                                 'cs2010', 'ma2108'])

def run4():
    s = noBacktoBackQueryv3(4, [], ['cs1010', 'st2131', 'cs1231', 'ma1101r','cs2020',
                                    'cs2010', 'ma2108'])

def run5():
    s = generalQueryv4(4, [], ['cs1010', 'st2131', 'cs1231', 'ma1101r','cs2020',
                                   'cs2010', 'ma2108'], "freeday")

def run6():
    s = generalQueryv4(4, [], ['cs1010', 'st2131', 'cs1231', 'ma1101r','cs2020',
                                   'cs2010', 'ma2108'], "nobacktoback")

def runAllTests():
    #func = [run1, run2, run3, run4, run5]
    func = [run5, run6]
    for f in func:
        benchmark(f)


runAllTests()
