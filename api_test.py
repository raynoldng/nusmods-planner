import requests
from sets import Set
import json
from z3 import *

ENV = "DEV" # faster to do everything offline, AY16-17S

# ModuleCode -> [Lessons]

## Helper functions
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
    #dictionary(lessontype,dictionary(classNo, timeList))
    return mydict

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

# returns free day constraint, x is a weekday from 0 to 4
def freeDay(x):
	day = range(x*24,(x+1)*24)
	return day + [i+120 for i in day]

# returns list of discrete timeslots based on hour-based indexing in a fortnight
# used for z3's distinct query. 0-119 first week, 120-239 second week.
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

def transformMod(modtuple):
    return (modtuple[0], splitIntoLessonTypes(modtuple[1]))

# list of (moduleCode, {transformedLessons}) tuples and returns imcomplete z3 query
def parseZ3Query(mods, numToTake, solver = Solver()):
    timetable = []
    selection = []
    numMods = len(mods)
    X = [Int("x_%s" % i) for i in range(numToTake)] # creates 5 indicators determining which modules we try
    solver.add(Distinct(X))
    solver.add([And(X[i] >= 0, X[i]<numMods) for i in range(numToTake)])
    for modIndex, mod in enumerate(mods):
        moduleCode = mod[0]
        constraints = []
        selected = Or([X[i] == modIndex for i in range(numToTake)]) #is this mod selected
        for lessonType, slots in mod[1].iteritems():
            firstFlag = True
            slotSelectors = []
            for slotName, timing in slots.iteritems():
                if firstFlag:
                    # add to timetable
                    timetable += [Int('%s_%s_%s' % (moduleCode, lessonType[:3], index))
                                  for index in range(len(timing))]
                    firstFlag = False
                selector = Bool('%s_%s_%s' % (moduleCode, lessonType[:3], slotName))
                selection.append(selector)
                slotSelectors.append(selector)

                selectionMapping[selector] = timing

                for index, time in enumerate(timing):
                    implicants = [Int('%s_%s_%s' % (moduleCode, lessonType[:3], index)) == time]
                    implication = Implies(selector, And(implicants))
                    constraints.append(implication)
            constraints.append(Or(Or(slotSelectors),Not(selected))) 
        # not selected then we don't care, tutorial for a mod we don't choose can be at -1945024 hrs
        # solver.add(Implies(selected, constraints))
        solver.add(constraints)
    print timetable
    print "there is should be something above"
    T = BitVec('T', 120)
    prevT = T
    for index, t in enumerate(timetable):
        newT = BitVec('T' + str(index), 120)
        solver.add(newT == prevT | 1 << t)
        prevT = newT

    # add the free day constraint
    # freeDayConstraint = Or([])

def timetableVisualizer(model, selectionMapping):
    timings = [v for k,v in selectionMapping.iteritems() if model[k]]
    timings = [item for sublist in timings for item in sublist]
    timings.sort()

    x = 0
    for i in timings:
        x |= 1 << i
    binstr = bin(x)[2:]
    binstr = binstr[::-1]  # reverse the string
    print binstr

def timetablePlanner(modsstr, numToTake):
    s = Solver()
    mods = [transformMod(query(m)) for m in modsstr]
    selection = parseZ3Query(mods, numToTake, s)
    if s.check() == sat:
        print "Candidate Timetable:"
        m = s.model()
        timetableVisualizer(m, selectionMapping)
        for s in selection:
            if m[s]:
                print str(s) + ' -> ' + str(selectionMapping[s])
    else:
        print "free day not possible"


# insert unit tests here, should shift them to a separate file later

def run():
    mod = query('st2131')
    mod = transformMod(mod)
    # parseZ3Query([mod])

    # timetablePlanner(['cs1010', 'st2131', 'cs1231', 'ma1101r', 'cs2100'])
    timetablePlanner(['cs1010', 'st2131', 'cs1231', 'ma1101r','cs2020','cs1020','cs2010'], 4)
    # f = open('out.txt', 'w')
    # print >> f, splitIntoLessonTypes(json.load(open('st2131.json')))
    # f2 = open('out2.txt', 'w')
    # print >> f2, splitIntoLessonTypes(query('st2131'))
    # f2.close()

    # f.close()
    #lessons = splitIntoLessonTypes(mod)
    #print lessons

    #print [Bool('b%s' % i) for i in range(5)]

    #print "\n\nPrinting Z3 bools"
    #parseZ3Query([lessons])

run()

