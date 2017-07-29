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

    def checkTimetable(self, timetable, options = {}):
        self.assertTrue(self.calendarUtils.scheduleValid(timetable))
        # NOTE deprecated
        if 'numFreedays' in options and options['numFreedays'] > 0:
            freedaysToAssert = []
            for d in options['freedays']:
                freedaysToAssert.append('%s %s' % ('Odd', d))
                freedaysToAssert.append('%s %s' % ('Even', d))
            freedaysInTimetable = self.calendarUtils.gotFreeDay(timetable)
            for d in freedaysToAssert:
                self.assertTrue(d in freedaysInTimetable)

        if 'freeday' in options and options['freeday']:
            freedays = self.calendarUtils.gotFreeDay(timetable)
            self.assertTrue(len(freedays) > 0)

            if 'possibleFreedays' in options and len(options['possibleFreedays']) > 0:
                possibleFreedays = options['possibleFreedays']
                gotDesiredFreeday = False
                for day in possibleFreedays:
                    if 'Even %s' % day in freedays and 'Odd %s' % day in freedays:
                        gotDesiredFreeday = True
                        break
                self.assertTrue(gotDesiredFreeday)

        if 'lockedLessonSlots' in options:
            lockedLessons = options['lockedLessonSlots']
            for lesson in lockedLessons:
                self.assertTrue(lesson in timetable)

        if 'lunchBreak' in options and options['lunchBreak']:
            timetableHours = self.calendarUtils.getHoursFromSchedule(timetable)
            for d in range(10):
                # check that not all lunch hours each day is taken up
                assert(len([d*24 + h for h in mod_utils.LUNCH_HOURS
                            if d*24 + h in timetableHours]) < len(mod_utils.LUNCH_HOURS))

    def testSpecificAndNonSpecificFreedays(self):
        ''' Verify that timetable contains the specified free day and another soft free day
        NOTE numFreedays is deprecated, not used in live version for now
        '''
        compMods = ['CS2100', 'CS1010', 'GEQ1000', 'GER1000']
        optMods = []
        options = {'numFreedays': 2, 'freedays': ['Tuesday']}
        timetable = querySolverBV.solveQuery(4, compMods, [], options, semester = SEMESTER)

        self.checkTimetable(timetable, options)

    def testSpecificFreedayandNoLessonsBefore(self):
        ''' Live version returned incorrectly unsat
        NOTE numFreedays is deprecated, not used in live version for now
        '''
        compMods = ['GEQ1000', 'PS2203', 'PS2237', 'PS3271', 'SN1101E']
        optMods = []
        options = {'numFreedays': 2, 'freedays': ['Monday', 'Tuesday'], 'noLessonsBefore': 8}
        numMods = 5
        timetable = querySolverBV.solveQuery(numMods, compMods, optMods, options, semester = SEMESTER)

        self.checkTimetable(timetable, options)

    def testFreeday(self):
        ''' Return a timetable that has at least one free day
        '''

        compMods = ['CS1231', 'CS2100', 'MA1101R', 'MA1102R']
        optMods = []
        numMods = 4
        options = {'freeday': True}
        timetable = querySolverBV.solveQuery(numMods, compMods, [], options, semester = SEMESTER)

        self.checkTimetable(timetable, options)

    def testFreedayFromSubset(self):
        ''' Return a timetable that has at least one free day from specified weekdays
        '''

        compMods = ['CS1231', 'CS2100', 'MA1101R', 'MA1102R']
        optMods = []
        numMods = 4
        options = {'freeday': True, 'possibleFreedays': ['Tuesday', 'Wednesday']}
        timetable = querySolverBV.solveQuery(numMods, compMods, [], options, semester = SEMESTER)

        self.checkTimetable(timetable, options)

    def testUndefinedTimetable(self):
        ''' some slots are undefined
        '''
        numMods = 4
        compMods = []
        optMods = ['GEQ1000', 'MA1101R', 'GER1000', 'MA1100', 'CS1010', 'CS1231']
        options = {'freeday': True, 'possibleFreedays': []}
        timetable = querySolverBV.solveQuery(numMods, compMods, optMods, options, semester = SEMESTER)

        self.checkTimetable(timetable, options)

    def testWeekendLessons(self):
        ''' Edge case where the module has weekend lessons (e.g. CG1111)
        '''
        numMods = 5
        optMods = ['CG1111', 'EN1101E', 'GE1101E', 'LA4203', 'MA1100', 'PC1141']
        compMods = []
        options = {}
        timetable = querySolverBV.solveQuery(numMods, compMods, optMods, options, semester = SEMESTER)

        self.checkTimetable(timetable, options)


    def testLunchHours(self):
        numMods = 5
        optMods = []
        compMods = ['CS1010', 'CS1231', 'GEQ1000', 'GER1000', 'MA1101R']
        options = {"lunchBreak":True}
        timetable = querySolverBV.solveQuery(numMods, compMods, optMods, options, semester = SEMESTER)

        self.checkTimetable(timetable, options)

if __name__ == '__main__':
    unittest.main()
# TODO add options to checkTimetable
