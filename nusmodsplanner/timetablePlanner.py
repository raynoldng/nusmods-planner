import sys
from querySolverBV import *
import mod_utils

numMods = int(sys.argv[1])
mods = sys.argv[2:]

schedule = timetablePlanner(mods, numMods)

print schedule
if schedule is not None:
    print "Possible Timetable:"
    for s in schedule:
        print s
    freeDays = mod_utils.gotFreeDay(schedule)
    print "Free days: " + ", ".join(freeDays)
