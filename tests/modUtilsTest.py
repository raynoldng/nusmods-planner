import unittest
import sys
from z3 import *
sys.path.append('../../nusmods-planner')
from nusmodsplanner.mod_utils import CalendarUtils

class modUtilsTest(unittest.TestCase):

    def setUp(self):
        self.CalendarUtils = CalendarUtils

    def test_correctly_imported(self):
        self.assertTrue(self.CalendarUtils != None)
        self.assertTrue(self.CalendarUtils.gotFreeDay != None)

    def test_modUtils_init(self):
        modUtils_AY1718S1 = self.CalendarUtils('AY1718S1')
        self.assertTrue(len(modUtils_AY1718S1._dict.keys()) > 0)

        modUtils_AY1617S2 = self.CalendarUtils('AY1617S2')
        self.assertTrue(len(modUtils_AY1617S2._dict.keys()) > 0)

        self.assertTrue(len(modUtils_AY1617S2._dict.keys()) != len(modUtils_AY1718S1._dict.keys()))

    def test_valid_schedule(self):
        calendarUtils = self.CalendarUtils('AY1617S2')
        print calendarUtils.gotFreeDay
        testSchedule = ['GEQ1000_Tutorial_56', 'CS1010_Sectional Teaching_31', 
                        'CS1010_Tutorial_C04', 'MA1102R_Laboratory_B11', 
                        'MA1102R_Tutorial_T09', 'MA1102R_Lecture_SL1', 
                        'MA1101R_Laboratory_B08', 'MA1101R_Tutorial_T17', 'MA1101R_Lecture_SL1']

        self.assertTrue(calendarUtils.scheduleValid(testSchedule))

if __name__ == '__main__':
    unittest.main()
