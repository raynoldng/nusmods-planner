# '''
# queryParseTest

# 1. hoursBefore
# 2. hoursAfter
# '''

import unittest
import sys
from z3 import *
sys.path.append('../nusmodsplanner')
import queryParserBV
import querySolverBV
import mod_utils

SEMESTER = 'AY1617S2'

class TestQueryParserBV(unittest.TestCase):

    def setUp(self):
        self.calendarUtils = mod_utils.CalendarUtils(SEMESTER)

    def testOutputValid(self):
        ''' Verify that output is indeed SMTLIB2 valid syntax and can be solved
        by a SMT solver
        '''
        optmods = ['CS1231', 'CS1020', 'CS2100', 'CS2020', 'CS2105', 'MA1101R', 
                   'ST2131']
        options = {'freeday': True}

        smtlib2, modmapping = queryParserBV.parseQuery(4, [], optmods, options, semester = SEMESTER)
        assertions = parse_smt2_string(smtlib2)
        s = Solver()
        s.add(assertions)
        self.assertEqual(s.check(), sat)

    def testFreedayQuery(self):
        ''' Verify that assertions represent a timetable with a freeday

        '''
        optmods = ['CS1231', 'CS1020', 'CS2100', 'CS2020', 'CS2105', 'MA1101R', 
                   'ST2131']
        options = {'freeday': True}
        timetable = querySolverBV.solveQuery(4, [], optmods, options, semester = SEMESTER)
        # print timetable
        # print mod_utils.gotFreeDay(timetable)
        self.assertTrue(self.calendarUtils.scheduleValid(timetable))
        self.assertTrue(len(self.calendarUtils.gotFreeDay(timetable)) > 0)

    def testNoFreeDay(self):
        ''' Verify that query returns unsat if a freeday is indeed impossible
        '''
        compmods = ['CS1010', 'CS1231', 'CS2105', 'ST2131']
        optmods = ['MA1101R', 'CS2020']
        options = {'freeday': True}
        timetable = querySolverBV.solveQuery(5, [], optmods, options, semester = SEMESTER)
        self.assertTrue(len(timetable) == 0)

    def testNoLessonBefore(self):
        '''Verify that assertions represent a timetable that has no lessons
        before the user defined time
        '''
        optmods = ['CS1231', 'CS1020', 'CS2100', 'CS2020', 'CS2105', 'MA1101R', 
                   'ST2131']
        options = {'noLessonsBefore': 12}
        timetable = querySolverBV.solveQuery(4, [], optmods, options, semester = SEMESTER)

        self.assertTrue(self.calendarUtils.scheduleValid(timetable))
        self.assertTrue(self.calendarUtils.checkNoLessonsBefore(timetable, 12))

    def testNoLessonAfter(self):
        '''Verify that assertions represent a timetable that has no lessons
        before the user defined time
        '''
        optmods = ['CS1231', 'CS1020', 'CS2100', 'CS2020', 'CS2105', 'MA1101R', 
                   'ST2131']
        options = {'noLessonsAfter': 19}
        timetable = querySolverBV.solveQuery(4, [], optmods, options, semester = SEMESTER)

        self.assertTrue(self.calendarUtils.scheduleValid(timetable))
        self.assertTrue(self.calendarUtils.checkNoLessonsAfter(timetable, 19))

    def testSatAndValidTimetable(self):
        ''' Returns empty (unsat) during test, should not be the case
        '''
        optmods = ['GEQ1000', 'CS1010', 'MA1102R', 'MA1101R']
        options = {}
        timetable = querySolverBV.solveQuery(4, [], optmods, options, semester = SEMESTER)
        print timetable
        self.assertTrue(self.calendarUtils.scheduleValid(timetable))
        self.assertTrue(self.calendarUtils.checkNoLessonsAfter(timetable, 19))

    def testSatAndValidTimetable2(self):
        ''' Returns empty (unsat) during test, should not be the case
        '''
        options = {'noLessonsAfter': 19, 'noLessonsBefore': 8}
        compmods = ['MA1101R', 'ACC1002', 'GER1000', 'GEQ1000']
        timetable = querySolverBV.solveQuery(4, compmods, [], options, semester = SEMESTER)
        print timetable
        self.assertTrue(self.calendarUtils.scheduleValid(timetable))
        self.assertTrue(self.calendarUtils.checkNoLessonsAfter(timetable, 19))

    def testLockedLessonSlots1(self):
        ''' Verify that lockedLessonSlots appear in the timetable
        '''
        lockedLessonSlots = ['MA1101R_Tutorial_T10']
        compMods = ['CS1231', 'CS1020', 'CS2100', 'CS2105', 'MA1101R']
        options = {'lockedLessonSlots': lockedLessonSlots}
        timetable = querySolverBV.solveQuery(5, compMods, [], options, semester = SEMESTER)
        print timetable
        self.assertTrue(self.calendarUtils.scheduleValid(timetable))
        self.assertTrue(lockedLessonSlots[0] in timetable)

    def testLockedLessonSlots2(self):
        ''' Verify that lockedLessonSlots appear in the timetable
        '''
        lockedLessonSlots = ['MA1101R_Tutorial_T10', 'CS1231_Sectional Teaching_1']
        compMods = ['CS1231', 'CS1020', 'CS2100', 'CS2105', 'MA1101R']
        options = {'lockedLessonSlots': lockedLessonSlots}
        timetable = querySolverBV.solveQuery(5, compMods, [], options, semester = SEMESTER)
        print timetable
        self.assertTrue(self.calendarUtils.scheduleValid(timetable))
        for slots in lockedLessonSlots:
            self.assertTrue(slots in timetable)

if __name__ == '__main__':
    unittest.main()
