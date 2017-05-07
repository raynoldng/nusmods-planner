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
	r = requests.get('http://api.nusmods.com/2016-2017/1/modules/' + code + '/timetable.json')
	r = r.json()
	return r

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
def parseZ3Query(mods, solver = Solver(), timetable = [], selection = []):
    selectionMapping = {} # maps selection to hours
    for mod in mods:
        moduleCode = mod[0]
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
                    solver.add(implication)
                solver.add(Or(slotSelectors))
    # want timetable to be distinct
    solver.add(Distinct(timetable))
    return selectionMapping

def freeDayChecker(solver, timetable):
    print "there is should be something"
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



def timetablePlanner(modsstr):
    s = Solver()
    mods = [transformMod(query(m)) for m in modsstr]
    for m in mods:
        print m
    selection = [] # selector variables
    timetable = [] # time assignments

    selectionMapping = parseZ3Query(mods, s, timetable, selection)
    print "Timetable for:" + str(modsstr)
    print s.check()
    print selection
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
    parseZ3Query([mod])

    # timetablePlanner(['cs1010', 'st2131', 'cs1231', 'ma1101r', 'cs2100'])
    result = timetablePlanner(['cs1010', 'st2131', 'cs1231', 'ma1101r'])
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

