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

class TestQueryParserBV(unittest.TestCase):

	def testOutputValid(self):
		''' Verify that output is indeed SMTLIB2 valid syntax and can be solved
		by a SMT solver
		'''
		optmods = ['CS1231', 'CS1020', 'CS2100', 'CS2020', 'CS2105', 'MA1101R', 
				   'ST2131']
		options = {'freeday': True}

	   	smtlib2, modmapping = queryParserBV.parseQuery(4, [], optmods, options)
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
		timetable = querySolverBV.solveQuery(4, [], optmods, options)
		# print timetable
		# print mod_utils.gotFreeDay(timetable)
		self.assertTrue(mod_utils.scheduleValid(timetable))
		self.assertTrue(len(mod_utils.gotFreeDay(timetable)) > 0)

	def testNoLessonBefore(self):
		'''Verify that assertions represent a timetable that has no lessons
		before the user defined time
		'''
		optmods = ['CS1231', 'CS1020', 'CS2100', 'CS2020', 'CS2105', 'MA1101R', 
				   'ST2131']
		options = {'noLessonsBefore': 12}
		timetable = querySolverBV.solveQuery(4, [], optmods, options)

		self.assertTrue(mod_utils.scheduleValid(timetable))
		self.assertTrue(mod_utils.checkNoLessonsBefore(timetable, 12))

	def testNoLessonAfter(self):
		'''Verify that assertions represent a timetable that has no lessons
		before the user defined time
		'''
		optmods = ['CS1231', 'CS1020', 'CS2100', 'CS2020', 'CS2105', 'MA1101R', 
				   'ST2131']
		options = {'noLessonsAfter': 19}
		timetable = querySolverBV.solveQuery(4, [], optmods, options)

		self.assertTrue(mod_utils.scheduleValid(timetable))
		self.assertTrue(mod_utils.checkNoLessonsAfter(timetable, 19))


if __name__ == '__main__':
    unittest.main()