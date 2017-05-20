import unittest
import sys
sys.path.append('../nusmodsplanner')
import querySolver
import mod_utils

class TestFreeDayQueries(unittest.TestCase):

    def testFreeDay5Mods(self):
        mods = ['CS1020', 'ST2131', 'MA1101R', 'CS2100', 'CS1231']
        schedule = querySolver.timetablePlanner(5, mods)
        self.assertEqual(True, mod_utils.scheduleValid(schedule))
        self.assertTrue(len(mod_utils.gotFreeDay(schedule)) > 0)

    def testSubsetofMods(self):
        mods = ['CS2020', 'ST2131', 'CS2100', 'MA1101R', 'CS1231', 'CS2105', 'CS1020']
        schedule = querySolver.timetablePlanner(5, mods)
        self.assertEqual(True, mod_utils.scheduleValid(schedule))
        self.assertTrue(len(mod_utils.gotFreeDay(schedule)) > 0)

if __name__ == '__main__':
    unittest.main()
