''' To test lesson locking functionality of solve,
merge into the main file when done
'''
import unittest
import sys
from z3 import *
sys.path.append('../nusmodsplanner')
import queryParserBV
import querySolverBV
import mod_utils

class TestQueryParserBV2(unittest.TestCase):

    def testLockedLessonSlots1(self):
        ''' Verify that lockedLessonSlots appear in the timetable
        '''
        lockedLessonSlots = ['MA1101R_Tutorial_T10']
        compMods = ['CS1231', 'CS1020', 'CS2100', 'CS2105', 'MA1101R']
        options = {'lockedLessonSlots': lockedLessonSlots}
        timetable = querySolverBV.solveQuery(5, compMods, [], options)
        print timetable
        self.assertTrue(mod_utils.scheduleValid(timetable))
        self.assertTrue(lockedLessonSlots[0] in timetable)

    def testLockedLessonSlots2(self):
        ''' Verify that lockedLessonSlots appear in the timetable
        '''
        lockedLessonSlots = ['MA1101R_Tutorial_T10', 'CS1231_Sectional Teaching_1']
        compMods = ['CS1231', 'CS1020', 'CS2100', 'CS2105', 'MA1101R']
        options = {'lockedLessonSlots': lockedLessonSlots}
        timetable = querySolverBV.solveQuery(5, compMods, [], options)
        print timetable
        self.assertTrue(mod_utils.scheduleValid(timetable))
        for slots in lockedLessonSlots:
            self.assertTrue(slots in timetable)
if __name__ == '__main__':
    unittest.main()
