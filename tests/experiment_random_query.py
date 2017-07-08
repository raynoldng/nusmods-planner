'''
For semester 1
Experiment to see if randomizing the queries will result in a new timetable
Note that this is not a strict requirement
'''
import unittest
import sys
from z3 import *
sys.path.append('../nusmodsplanner')
import queryParserBV
import querySolverBV
import mod_utils
import random

SEMESTER = 'AY1718S1'

def isScheduleSame(t1, t2):
    t1.sort()
    t2.sort()
    return str(t1) == str(t2)

class TestQueryParserBV(unittest.TestCase):

    def setUp(self):
        self.calendarUtils = mod_utils.CalendarUtils(SEMESTER)

    # def testModUtilsShuffle(self):
    #     a = self.calendarUtils.queryAndTransform('CS1010');
    #     # print a

    def testisScheduleSame(self):
        testSchedule = ['GEQ1000_Tutorial_56', 'CS1010_Sectional Teaching_31', 
                        'CS1010_Tutorial_C04', 'MA1102R_Laboratory_B11', 
                        'MA1102R_Tutorial_T09', 'MA1102R_Lecture_SL1', 
                        'MA1101R_Laboratory_B08', 'MA1101R_Tutorial_T17', 'MA1101R_Lecture_SL1']
        self.assertTrue(isScheduleSame(testSchedule, testSchedule))
    def testSpecificAndNonSpecificFreedays(self):
        ''' Verify that timetable contains the specified free day and another soft free day
        '''
        compMods = ['CS2100', 'CS1010', 'GEQ1000', 'GER1000']
        optMods = []
        options = {'numFreedays': 2, 'freedays': ['Tuesday']}
        timetable1 = querySolverBV.solveQuery(4, compMods, [], options, semester = SEMESTER)
        print timetable1

        # random.shuffle(compMods)
        # print compMods
        timetable2 = querySolverBV.solveQuery(4, compMods, [], options, semester = SEMESTER)
        print timetable2

        print isScheduleSame(timetable1, timetable2)

if __name__ == '__main__':
    unittest.main()
