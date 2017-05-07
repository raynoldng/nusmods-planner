import requests
from sets import Set
import json
from z3 import *

ENV = "DEV" # faster to do everything offline, AY16-17S

if ENV == "DEV":
    _mods = json.load(open('timetable.json'))
    _dict = {x['ModuleCode']: x['Timetable'] for x in _mods if 'Timetable' in x}

# modjson: json object
def splitIntoLessonTypes(mod):
    lessonTypes = Set([i['LessonType'] for i in mod])
    mydict = {}
    for i in lessonTypes:
    	mydict[i] = {}
    for lst in mod:
    	tList = timeList(lst["WeekText"], lst["DayText"], lst["StartTime"], lst["EndTime"])
    	classId = lst['ClassNo']
    	lType = lst['LessonType']
    	if classId in mydict[lType].keys():
    		mydict[lType][classId] = mydict[lType][classId] + tList
    	else:
    		mydict[lType][classId] = tList
    return mydict

# Sample API call:
# http://api.nusmods.com/2016-2017/1/modules/ST2131/timetable.json
# returns tuple of (ModuleCode, [{Lessons for each type}])
def query(code):
    code = code.upper() # codes are in upper case
    # if in DEV mode then pull everything from local sources
    if ENV == "DEV":
        #return _dict[code]
        return (code, _dict[code])
    # TODO test online API
    # might have broken the online one
	r = requests.get('http://api.nusmods.com/2016-2017/1/modules/' + code.upper() + '/timetable.json')
	r = r.json()
	return r

# returns list of hours corresponding to day of the week for even and odd week
def freeDay(x):
	day = range(x*24,(x+1)*24)
	return day + [i+120 for i in day]

# returns list of discrete timeslots based on hour-based indexing in a fortnight
# used for z3's distinct query. 0-119 first week, 120-239 second week.
# 24 hours in a day
def timeList(weektext, daytext, starttime, endtime):
    #some hard code
    weekdays = {"Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3, "Friday": 4}
    ofst = weekdays[daytext]*24
    lst = [i+ofst for i in range(int(starttime)/100, int(endtime)/100)]
    if (weektext == "Odd Week"):
        return lst
    elif (weektext == "Even Week"):
        return [i+120 for i in lst]
    # default every week
    else:
        return [i+120 for i in lst]+lst


# returns selection: list of all lesson slots for us to iterate through the model to find schedule
def parseZ3Query(mods, numToTake, solver = Solver()):
    timetable = [] # contains the symbolic work hours for all mods
    selection = [] # represents all the lecture, rec slots etc
    numMods = len(mods)

    # numMods choose numToTake
    # creates indicators determining which modules we try
    X = [Int("x_%s" % i) for i in range(numToTake)]
    # assert that mods are distinct and have legal indices
    solver.add(Distinct(X))
    solver.add([And(X[i] >= 0, X[i]<numMods) for i in range(numToTake)])

    for modIndex, mod in enumerate(mods):
        moduleCode = mod[0]
        constraints = []
        selected = Or([X[i] == modIndex for i in range(numToTake)]) # is this mod selected

        # iterate through all timeslots and parse the implications
        # Each hours of the timeslot is represented as one z3 IntSort
        for lessonType, slots in mod[1].iteritems():
            firstFlag = True
            slotSelectors = [] # selector variable for timeslot
            for slotName, timing in slots.iteritems():
                if firstFlag:
                    # add to timetable, symbolic hour timeslot
                    timetable += [Int('%s_%s_%s' % (moduleCode, lessonType, index))
                                  for index in range(len(timing))]
                    firstFlag = False
                selector = Bool('%s_%s_%s' % (moduleCode, lessonType, slotName))
                selection.append(selector)
                slotSelectors.append(selector)
                # add implications if particular timeslot is selected
                for index, time in enumerate(timing):
                    # it is fine to repeat variable names, z3 maps to the same variable
                    implicants = [Int('%s_%s_%s' % (moduleCode, lessonType, index)) == time]
                    implication = Implies(selector, And(implicants))
                    constraints.append(implication)
            # pick one timeslot from each timeslot, or ignore if mod is not chosen
            constraints.append(Or(Or(slotSelectors),Not(selected)))
        # not selected then we don't care, tutorial for a mod we don't choose can be at -1945024 hrs
        solver.add(constraints)
    solver.add(Or([Distinct(timetable+freeDay(i)) for i in range(5)]))
    return selection

def timetablePlanner(modsstr, numToTake):
    def transformMod(modtuple):
        return (modtuple[0], splitIntoLessonTypes(modtuple[1]))
    s = Solver()
    mods = [transformMod(query(m)) for m in modsstr]
    selection = parseZ3Query(mods, numToTake, s)
    if s.check() == sat:
        print "Candidate Timetable:"
        m = s.model()
        schedule = [str(s) for s in selection if m[s]]
    else:
        print "free day not possible"


# insert unit tests here, should shift them to a separate file later

def run():
    timetablePlanner(['cs1010', 'st2131', 'cs1231', 'ma1101r','cs2020','cs1020','cs2010'], 4)

run()

