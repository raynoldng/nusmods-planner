# helper functions for testing properties of candidate schedules
import requests
from sets import Set
import json
import calendar
import itertools

ENV = "DEV" # faster to do everything offline, AY16-17S

if ENV == "DEV":
    _mods = json.load(open('../data/timetable.json'))
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
    """FIXME! briefly describe function

    :param weektext: 
    :param daytext: 
    :param starttime: 
    :param endtime: 
    :returns: 
    :rtype: 

    """
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

# first, some hard code for testing, science mapped to 0, arts to 1, computing to 2, utown to 3, etc. does not yet cover all cases.
# ideally this will eventually be a dictionary so that venuecode retrieval is constant. for generation of this dictionary,
# we intend to do this recursively, adding all the keys following a certain expression, printing out all venues that are not in dict,
# finding general expressions for a subset of those, adding them to the dict and so on. this will probably have to be done manually,
# as the current venue mappings are way too specific (in nusmods API - rawvenues)

def VenueMap(str):
    ustr = str.upper()
    if ustr[0] == "S":
        return 0
    elif ustr[:2] == "AS":
        return 1
    elif ustr[:3] == "COM":
        return 2
    elif ustr[:2] == "UT" or ustr[:3] == "ERC":
    	return 3
    elif ustr[:2] == "LT": # i know this is wrong but this is just for testing
    	return 4
    else:
        print str

def test(modslist):
	ttlist = [query(a) for a in modslist]
	for tt in ttlist:
		for a in tt[1]:
			# print a["Venue"]
			VenueMap(a["Venue"])
	print VenueMap("wowas6-4")

# returns a dictionary mapping venues to their cluster - 0: Science, 1: Computing/Business/I3, 2: Engineering, 3: Arts, 4: 
# manual updating is possible
# intending to slowly update m_dict here using if else and prefix matching, then commenting it out so the process is faster
def generateVenueCodes(venuepath, dictpath):
	file = open(venuepath, "r")
	lines = file.readlines()
	lines = [r.rstrip().upper() for r in lines]
	m_dict = json.load(open(dictpath))
	print m_dict
	for venue in lines:
		if venue not in m_dict:
			pass # add key value pairs to m_dict here
		else:
			print venue + ": " + str(m_dict[venue]) # for debugging
	file2 = open(dictpath, "w") # clears file
	json.dump(m_dict,file2)
	file.close()
	file2.close()

lst = ['st2131', 'cs1010', 'cs2020', 'cs2010', 'cs1020', 'ma1101r', 'ma2101s', 'ma1104']
test(lst)
# print queryAndTransform("st2131", "includevenues")
generateVenueCodes('../data/venues.txt', '../data/venuecodes.json')

