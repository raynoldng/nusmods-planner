''' For AY1718S1
'''
import unittest
import sys
from z3 import *
sys.path.append('../nusmodsplanner')
import queryParserBV
import querySolverBV
import mod_utils

SEMESTER = 'AY1718S1'

class TestQueryParserBV(unittest.TestCase):

    def setUp(self):
        self.calendarUtils = mod_utils.CalendarUtils(SEMESTER)

    def testSpecificAndNonSpecificFreedays(self):
        ''' Verify that timetable contains the specified free day and another soft free day
        '''
        compMods = ['CS2100', 'CS1010', 'GEQ1000', 'GER1000']
        optMods = []
        options = {'numFreedays': 2, 'freedays': ['Tuesday']}
        timetable = querySolverBV.solveQuery(4, compMods, [], options, semester = SEMESTER)
        print timetable
        self.assertTrue(self.calendarUtils.scheduleValid(timetable))
        freedays = self.calendarUtils.gotFreeDay(timetable)
        print freedays
        for d in ['Even Tuesday', 'Odd Tuesday']:
            self.assertTrue(d in freedays)
        # assert that we get another free day on top of the indicated Tuesday
        self.assertTrue(len(self.calendarUtils.gotFreeDay(timetable)) > 2)

    def testSpecificFreedayandNoLessonsBefore(self):
        ''' Live version returned incorrectly unsat
        '''
        compMods = ['GEQ1000', 'PS2203', 'PS2237', 'PS3271', 'SN1101E']
        optMods = []
        options = {'numFreedays': 2, 'freedays': ['Monday', 'Tuesday'], 'noLessonsBefore': 8}
        numMods = 5

        timetable = querySolverBV.solveQuery(numMods, compMods, optMods, options, semester = SEMESTER)
        self.assertTrue(self.calendarUtils.scheduleValid(timetable))
        freedays = self.calendarUtils.gotFreeDay(timetable)
        print freedays
        for d in ['Even Monday', 'Odd Monday', 'Even Tuesday', 'Odd Tuesday']: self.assertTrue(d in freedays)
        print timetable
if __name__ == '__main__':
    unittest.main()
