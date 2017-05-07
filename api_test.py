import requests
from sets import Set
import json
from z3 import *

ENV = "DEV" # faster to do everything offline

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
def parseZ3Query(mods, solver = Solver()):
    timetable = []
    for mod in mods:
        moduleCode = mod[0]
        for lessonType, slots in mod[1].iteritems():
            firstFlag = True
            slotSelectors = []
            for slotName, timing in slots.iteritems():
                if firstFlag:
                    # add to timetable
                    timetable += [Int('%s_%s_%s' % (moduleCode, lessonType, index))
                                  for index in range(len(timing))]
                    firstFlag = False
                for index, time in enumerate(timing):
                    selector = Bool('%s_%s_%s' % (moduleCode, lessonType[:3], slotName))
                    slotSelectors.append(selector)
                    implicants = [Int('%s_%s_%s' % (moduleCode, lessonType, index)) == time]
                    implication = Implies(selector, And(implicants))
                    solver.add(implication)
                solver.add(Or(slotSelectors))
    print timetable
    # want timetable to be distinct
    solver.add(Distinct(timetable))
    print solver
    print solver.check()


# list of (moduleCode, {transformedLessons}) tuples and returns imcomplete z3 query
def parseZ3Query2(mods, solver = Solver()):
    for mod in mods:
        moduleCode = mod[0]
        lessons = mod[1]
        for lessonType, timings in lessons.iteritems():
            print lessonType
            slotSelectors = [Bool('%s_%s_%s' % (moduleCode, lessonType[:3], time)) for time in timings]
            # print timings for each time slot
            print [v for k,v in timings.iteritems()]


            # create symbolic variables representing lessonSlots
            # assumption is that all slots are of the same length
            lessonSlotLength = len(timings.values()[0])
            symbolicLessonSlots = [Int('%s_%s%s' % (moduleCode, lessonType[:3], i))
                                   for i in range(lessonSlotLength)]
            print symbolicLessonSlots

            # create the implications
            imps = []
            
# insert unit tests here, should shift them to a separate file later
def run():
    mod = query('st2131')
    mod = transformMod(mod)
    print mod
    parseZ3Query([mod])
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

