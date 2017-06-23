# helper functions for testing properties of candidate schedules
import requests
from sets import Set
import json
import calendar
import itertools
import os
from definitions import ROOT_DIR
from z3 import *
ENV = "DEV" # faster to do everything offline, AY16-17S

if ENV == "DEV":
    pathToData = os.path.join(ROOT_DIR, '../data/timetable.json')
    _mods = json.load(open(pathToData))
    _dict = {x['ModuleCode']: x['Timetable'] for x in _mods if 'Timetable' in x}

def modsListToLessonMapping(transformedModsLst):
    # prepare list of mod -> lessons -> slots
    val = {i[0]: {k:v.keys() for k, v in i[1].items()} for i in transformedModsLst}
    return val
# Sample API call:
# http://api.nusmods.com/2016-2017/1/modules/ST2131/timetable.json
# returns tuple of (ModuleCode, [{Lessons for each type}])
def query(code):
    code = code.upper() # codes are in upper case
    # if in DEV mode then pull everything from local sources
    if ENV == "DEV":
        return (code, _dict[code])
    # TODO test online API
    r = requests.get('http://api.nusmods.com/2016-2017/1/modules/' + code.upper() + '/timetable.json')
    r = r.json()
    return r

def timeList(weektext, daytext, starttime, endtime):
    """Returns list of discrete timeslots based on hour-based indexing in a
    fortnight used for z3's distinct query. 0-119 first week, 120-239 second week. 24 hours in a day

    :param weektext: Odd/Even Week
    :param daytext: day of the week
    :param starttime: 24h format
    :param endtime: 24h format
    :returns: list of hour slots
    :rtype: list

    """
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
def splitIntoLessonTypes(mod, option = ""):
    if option == "":
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
    elif option == "includevenues":
        lessonTypes = Set([i['LessonType'] for i in mod])
        m_dict = {}
        for i in lessonTypes:
           m_dict[i] = {}
        for lst in mod:
            tList = timeList(lst["WeekText"], lst["DayText"], lst["StartTime"], lst["EndTime"])
            classId = lst['ClassNo']
            lType = lst['LessonType']
            venue = lst['Venue']
            if classId in m_dict[lType].keys():
                m_dict[lType][classId][0] = m_dict[lType][classId][0] + tList
            else:
                m_dict[lType][classId] = [tList, venue]
	    		# here we are assuming each ClassNo only has one venue, or if they have different venues, they are in the same cluster
        return m_dict
    else:
        return "unknown option"

def transformMod(modtuple):
    return (modtuple[0], splitIntoLessonTypes(modtuple[1]))

def queryAndTransform(moduleCode, option = ""):
    modtuple = query(moduleCode)
    return (modtuple[0], splitIntoLessonTypes(modtuple[1], option))

def outputFormatter(model, numToTake, modlst):
    for i in range(numToTake):
        modIndex = model[Int("x_%s" % i)].as_long()
        mod = modlst[modIndex]
        moduleCode = mod[0]
        for lessonType, slots in mod[1].iteritems():
            chosenSlot = model[Int('%s_%s' % (moduleCode, lessonType[:3]))].as_long()
            slotName = slots[chosenSlot][0]
            print "%s_%s_%s" % (moduleCode, lessonType[:3], slotName)

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

def getHours(lesson):
    """Returns list of hours from lesson slot, e.g. 'ST2131_Lecture_SL1'

    :param lesson: (str) lesson slot of format [module code]_[lesson type]_[lesson code]
    :returns: list of hours (from 240 hours based indexing)
    :rtype: list

    """
    mod, lessonType, slot = lesson.split('_')
    modJSON = queryAndTransform(mod)[1]
    return modJSON[lessonType][slot]

def scheduleValid(schedule):
    """Returns true if schedule is valid, one of each lesson type and no clash

    :param schedule: list of lesson slots taken
    :returns: true if valid, false otherwise
    :rtype: Boolean

    """
    # check if lesson types of each covered
    mods = Set([s.split('_')[0] for s in schedule])
    # get jsons of each mods
    modsJSON = [query(m)[1] for m in mods]
    allLessonTypes = Set()
    for mod in mods:
        modJSON = query(mod)[1]
        for lesson in modJSON:
            allLessonTypes.add(mod + '_' + str(lesson['LessonType']))

    # get set of all lesson types in schedule
    scheduleLessonType = Set(["_".join(l.split('_')[:2]) for l in schedule])

    if len(allLessonTypes.symmetric_difference(scheduleLessonType)) != 0:
        return False

    # check that all hours are unique
    hours = [getHours(s) for s in schedule]
    combinedHours = list(itertools.chain.from_iterable(hours))
    return len(combinedHours) == len(Set(combinedHours))

def run():
    """Sample Usage

    :returns: 
    :rtype: 

    """
    testSchedule = ['ST2131_Lecture_SL1', 'ST2131_Tutorial_T1', 'MA1101R_Laboratory_B03',
                    'MA1101R_Tutorial_T06', 'MA1101R_Lecture_SL1', 'CS1020_Laboratory_7',
                    'CS1020_Sectional Teaching_1', 'CS1020_Tutorial_14', 'CS2010_Laboratory_4',
                    'CS2010_Tutorial_8', 'CS2010_Lecture_1']
    print gotFreeDay(testSchedule)
    print scheduleValid(testSchedule)

    def test(modslist):
        ttlist = [query(a) for a in modslist]
        for tt in ttlist:
            for a in tt[1]:
                # print a["Venue"]
                VenueMap(a["Venue"])
        print VenueMap("wowas6-4")

    lst = ['st2131', 'cs1010', 'cs2020', 'cs2010', 'cs1020', 'ma1101r', 'ma2101s', 'ma1104']
    test(lst)
    # print queryAndTransform("st2131", "includevenues")
    # generateVenueCodes('../data/venues.txt', '../data/venuecodes.json')


