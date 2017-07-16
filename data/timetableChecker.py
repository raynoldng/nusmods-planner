''' For checking output of timetable
'''
import sys
from z3 import *
sys.path.append('../../nusmods-planner')
from nusmodsplanner.mod_utils import CalendarUtils

mod_utils = CalendarUtils('AY1718S1')
timetable = ["MA1102R_Lecture_SL1", "MA1102R_Tutorial_T04", "MA1102R_Laboratory_B06", "CS1231_Tutorial_15", "CS1231_Sectional Teaching_2", "GER1000_Tutorial_S05", "MA1100_Tutorial_T06", "MA1100_Lecture_SL1"]

print "valid? " + str(mod_utils.scheduleValid(timetable))
print "freeday? " + str(mod_utils.gotFreeDay(timetable))