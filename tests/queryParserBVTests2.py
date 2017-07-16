'''
For semester 1
NOTE!

Specifying the number of freedays and specifying the free days has been deprecated.
Instead the query asserts that freeday is one of the specified
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

    def testTwoSpecificFreedays(self):
        ''' 2 specified free days
        '''
        compMods = ['CS1010', 'CS1231', 'GER1000', 'MA1101R']
        optMods = []
        options = {'numFreedays': 2, 'freedays': ['Tuesday', 'Wednesday']}
        timetable = querySolverBV.solveQuery(4, compMods, [], options, semester = SEMESTER)
        print timetable
        self.assertTrue(self.calendarUtils.scheduleValid(timetable))
        freedays = self.calendarUtils.gotFreeDay(timetable)
        print freedays
        for d in ['Even Tuesday', 'Odd Tuesday', 'Even Wednesday', 'Odd Wednesday']:
            self.assertTrue(d in freedays)

    def testTwoSpecificFreedays2(self):
        ''' 2 specified free days
        '''
        compMods = ['CS1010', 'CS1231', 'GER1000', 'MA1101R']
        optMods = []
        options = {'numFreedays': 2, 'freedays': ['Monday', 'Wednesday']}
        timetable = querySolverBV.solveQuery(4, compMods, [], options, semester = SEMESTER)
        print timetable
        self.assertTrue(self.calendarUtils.scheduleValid(timetable))
        freedays = self.calendarUtils.gotFreeDay(timetable)
        print freedays
        for d in ['Even Monday', 'Odd Monday', 'Even Wednesday', 'Odd Wednesday']:
            self.assertTrue(d in freedays)

    def testFreeday(self):
        ''' Return a timetable that has at least one free day
        '''

        compMods = ['CS1231', 'CS2100', 'MA1101R', 'MA1102R']
        optMods = []
        numMods = 4
        options = {'freeday': True}
        timetable = querySolverBV.solveQuery(numMods, compMods, [], options, semester = SEMESTER)
        print 'testFreeday'
        print timetable
        self.assertTrue(self.calendarUtils.scheduleValid(timetable))
        freedays = self.calendarUtils.gotFreeDay(timetable)
        print freedays
        self.assertTrue(len(freedays) >= 2)

    def testFreedayFromSubset(self):
        ''' Return a timetable that has at least one free day from specified weekdays
        '''

        compMods = ['CS1231', 'CS2100', 'MA1101R', 'MA1102R']
        optMods = []
        numMods = 4
        options = {'freeday': True, 'possibleFreedays': ['Tuesday', 'Wednesday']}
        timetable = querySolverBV.solveQuery(numMods, compMods, [], options, semester = SEMESTER)
        print 'testFreedayFromSubset'
        print timetable
        self.assertTrue(self.calendarUtils.scheduleValid(timetable))
        freedays = self.calendarUtils.gotFreeDay(timetable)
        print freedays
        isMondayFree = 'Even Monday' in freedays and 'Odd Monday' in freedays
        isTuesdayFree = 'Even Tuesday' in freedays and 'Odd Tuesday' in freedays
        self.assertTrue(isMondayFree or isTuesdayFree)


if __name__ == '__main__':
    unittest.main()
