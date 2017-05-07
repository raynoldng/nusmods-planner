# helper functions for testing properties of candidate schedules
import requests
from sets import Set
import json
import calendar

ENV = "DEV" # faster to do everything offline, AY16-17S

if ENV == "DEV":
    _mods = json.load(open('timetable.json'))
    _dict = {x['ModuleCode']: x['Timetable'] for x in _mods if 'Timetable' in x}


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

def transformMod(modtuple):
    return (modtuple[0], splitIntoLessonTypes(modtuple[1]))

def queryAndTransform(moduleCode):
    modtuple = query(moduleCode)
    return (modtuple[0], splitIntoLessonTypes(modtuple[1]))

# takes in a list of slots and returns lists of free days
def gotFreeDay(schedule):
    modCodes = Set([s.split('_')[0] for s in schedule])
    mods = [queryAndTransform(m) for m in modCodes]
    mods = dict((m[0], m[1]) for m in mods)
    # get list of hours
    hours = []
    for slot in schedule:
        mod, lessonType, slotName = slot.split('_')
        hours += mods[mod][lessonType][slotName]
    hours.sort()
    print hours

    hoursTwoWeeks = [[] for i in range(2 * 5)]
    for h in hours:
        hoursTwoWeeks[h / 24].append(h % 24)
    freeDays = []
    for i, day in enumerate(hoursTwoWeeks):
        if len(day) == 0:
            if i < 5:
                freeDays.append('Even ' + calendar.day_name[i % 5])
            else:
                freeDays.append('Odd ' + calendar.day_name[i % 5])
    return freeDays

def run():
    testSchedule = ['ST2131_Lecture_SL1', 'ST2131_Tutorial_T1', 'MA1101R_Laboratory_B03',
                    'MA1101R_Tutorial_T06', 'MA1101R_Lecture_SL1', 'CS1020_Laboratory_7',
                    'CS1020_Sectional Teaching_1', 'CS1020_Tutorial_14', 'CS2010_Laboratory_4',
                    'CS2010_Tutorial_8', 'CS2010_Lecture_1']
    print gotFreeDay(testSchedule)

# run()
