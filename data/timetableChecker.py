''' For checking output of timetable
'''
import sys
from z3 import *
sys.path.append('../nusmodsplanner')
import mod_utils

timetable = ["CS1010_Tutorial_3", "GEQ1000_Tutorial_56", "MA1101R_Lecture_SL1", "MA1101R_Tutorial_T11", "MA1101R_Laboratory_B02", "MA1102R_Lecture_SL1", "MA1102R_Tutorial_T03", "MA1102R_Laboratory_B01"]

print "valid? " + str(mod_utils.scheduleValid(timetable))
print "freeday? " + str(mod_utils.gotFreeDay(timetable))