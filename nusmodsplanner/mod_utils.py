# helper functions for testing properties of candidate schedules
import requests
from sets import Set
import json
import calendar
import itertools
import os
from collections import OrderedDict
import random
from definitions import ROOT_DIR, lessonTypeCodes
from z3 import *


def lessonTypeToCode(lessonType):
    if "freeday" in lessonType:
        return int(lessonType[-1])
    return lessonTypeCodes[lessonType]

def freeDay(x):
    day = range(x*24,(x+1)*24)
    return day + [i+120 for i in day]

def hoursBefore(x):
    hours = [range(i * 24, i * 24 + x) 
                      + range(120 + i * 24, 120 + i * 24 + x) 
                      for i in range(0,5)]
    hours = [i for sublist in hours for i in sublist]
    return hours

def hoursAfter(x):
    hours = [range(i * 24 + x, (i + 1) * 24) 
                      + range(120 + i * 24 + x, 120 + (i + 1) * 24) 
                      for i in range(0,5)]
    hours = [i for sublist in hours for i in sublist]
    return hours
def transformMod(modtuple):
        return (modtuple[0], splitIntoLessonTypes(modtuple[1]))

def outputFormatter(model, numToTake, modlst):
    for i in range(numToTake):
        modIndex = model[Int("x_%s" % i)].as_long()
        mod = modlst[modIndex]
        moduleCode = mod[0]
        for lessonType, slots in mod[1].iteritems():
            chosenSlot = model[Int('%s_%s' % (moduleCode, lessonType[:3]))].as_long()
            slotName = slots[chosenSlot][0]
            print "%s_%s_%s" % (moduleCode, lessonType[:3], slotName)

def modsListToLessonMapping(transformedModsLst):
    # prepare list of mod -> lessons -> slots
    val = {i[0]: {k:v.keys() for k, v in i[1].items()} for i in transformedModsLst}
    return val

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

def splitIntoLessonTypes(mod, option = ""):
    def shuffle_dict(d):
        keys = d.keys()
        random.shuffle(keys)
        return dict(OrderedDict([(k, d[k]) for k in keys]))
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
        # EXPERIMENT: shuffle to attempt to get a new schedule
        mydict = {k:shuffle_dict(v) for k,v in mydict.iteritems()}
        return mydict
    # elif option == "includevenues":
    #     lessonTypes = Set([i['LessonType'] for i in mod])
    #     m_dict = {}
    #     for i in lessonTypes:
    #        m_dict[i] = {}
    #     for lst in mod:
    #         tList = timeList(lst["WeekText"], lst["DayText"], lst["StartTime"], lst["EndTime"])
    #         classId = lst['ClassNo']
    #         lType = lst['LessonType']
    #         venue = lst['Venue']
    #         if classId in m_dict[lType].keys():
    #             m_dict[lType][classId][0] = m_dict[lType][classId][0] + tList
    #         else:
    #             m_dict[lType][classId] = [tList, venue]
    #             # here we are assuming each ClassNo only has one venue, or if they have different venues, they are in the same cluster
    #     return m_dict
    else:
        return "unknown option"

def freedayMod(numFreedays, freedays = []):
    ''' returns a mod tuple in the same internal representation used to solve timetable query
    freedays is an array of weekdays to keep free
    '''
    weekdays = {"Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3, "Friday": 4}
    freedayNumbers = [weekdays[day] for day in freedays]
    lessonSlots1 = {"freeday-%s" % i : [(str(d), freeDay(d)) for d in freedayNumbers]
                    for i in range(0, len(freedays))}
    lessonSlots2 = {"freeday-%s" % i : [(str(d), freeDay(d)) for d in range(5)]
                    for i in range(len(freedays), numFreedays)}
    lessonSlots1.update(lessonSlots2)
    return ['FREEDAY', lessonSlots1]

class CalendarUtils:
    ''' This class should only contain functions that require the timetable data
    '''
    def __init__(self, semester = 'AY1718S1'):
        pathToData = os.path.join(ROOT_DIR, '../data/' + semester + '_timetable.json')
        self.BASE_URL = 'http://api.nusmods.com/20' + semester[2:4] + '-20' + semester[4:6] + '/' + \
        semester[-1] + '/modules/'
        # self._dict = json.load(open(pathToData))

    
    # Sample API call:
    # http://api.nusmods.com/2016-2017/1/modules/ST2131/timetable.json
    # returns tuple of (ModuleCode, [{Lessons for each type}])
    def query(self, code):
        code = code.upper() # codes are in upper case
        # # if in DEV mode then pull everything from local sources
        # if code in self._dict:
        #     return (code, self._dict[code])

        url = self.BASE_URL + code.upper() + '/timetable.json'
        r = requests.get(self.BASE_URL + code.upper() + '/timetable.json')
        r = r.json()
        return (code, r)

    def queryAndTransform(self, moduleCode, option = ""):
        modtuple = self.query(moduleCode)
        return (modtuple[0], splitIntoLessonTypes(modtuple[1], option))
    
    # takes in a list of slots and returns lists of free days
    def gotFreeDay(self, schedule):
        schedule = [s for s in schedule if 'FREEDAY' not in s]
        modCodes = Set([s.split('_')[0] for s in schedule])
        mods = [self.queryAndTransform(m) for m in modCodes]
        mods = dict((m[0], m[1]) for m in mods)
        # get list of hours
        hours = []
        for slot in schedule:
            mod, lessonType, slotName = slot.split('_')
            if mod == 'FREEDAY':
                continue
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

    def getHours(self, lesson):
        """Returns list of hours from lesson slot, e.g. 'ST2131_Lecture_SL1'

        :param lesson: (str) lesson slot of format [module code]_[lesson type]_[lesson code]
        :returns: list of hours (from 240 hours based indexing)
        :rtype: list

        """
        mod, lessonType, slot = lesson.split('_')
        modJSON = self.queryAndTransform(mod)[1]
        return modJSON[lessonType][slot]

    def scheduleValid(self, schedule):
        """Returns true if schedule is valid, one of each lesson type and no clash

        :param schedule: list of lesson slots taken
        :returns: true if valid, false otherwise
        :rtype: Boolean

        """
        if len(schedule) == 0:
            return False
        # check if lesson types of each covered
        schedule = [s for s in schedule if "FREEDAY" not in s]
        mods = Set([s.split('_')[0] for s in schedule])
        # get jsons of each mods
        modsJSON = [self.query(m)[1] for m in mods]
        allLessonTypes = Set()
        for mod in mods:
            modJSON = self.query(mod)[1]
            for lesson in modJSON:
                allLessonTypes.add(mod + '_' + str(lesson['LessonType']))

        # get set of all lesson types in schedule
        scheduleLessonType = Set(["_".join(l.split('_')[:2]) for l in schedule])

        if len(allLessonTypes.symmetric_difference(scheduleLessonType)) != 0:
            return False

        # check that all hours are unique
        hours = [self.getHours(s) for s in schedule]
        combinedHours = list(itertools.chain.from_iterable(hours))
        return len(combinedHours) == len(Set(combinedHours))

    def checkNoLessonsBefore(self, schedule, hour):
        """ Returns true if schedule does not have any lessons before input hour
        """

        hours = hoursBefore(hour)
        # check that there not clashed between timetable and "illegal hours"
        timetableHours = [self.getHours(s) for s in schedule]
        combinedHours = list(itertools.chain.from_iterable(timetableHours))

        illegalHours = Set(hours)
        timetable = Set(combinedHours)

        if(len(illegalHours.intersection(timetable)) > 0):
            return False
        else:
            return True

    def checkNoLessonsAfter(self, schedule, hour):
        """ Returns true if schedule does not have any lessons before input hour
        """

        hours = hoursAfter(hour)
        # check that there not clashed between timetable and "illegal hours"
        timetableHours = [self.getHours(s) for s in schedule]
        combinedHours = list(itertools.chain.from_iterable(timetableHours))

        illegalHours = Set(hours)
        timetable = Set(combinedHours)

        if(len(illegalHours.intersection(timetable)) > 0):
            return False
        else:
            return True
