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
'''
Sample Output
[('CS1010', {u'Sectional Teaching': {u'1': [156, 157, 158, 36, 37, 38]}, u'Tutorial': {u'1': [226, 227, 1
06, 107], u'3': [230, 231, 110, 111], u'2': [228, 229, 108, 109]}}), ('ST2131', {u'Lecture': {u'SL1': [13
8, 139, 18, 19, 210, 211, 90, 91], u'SL2': [154, 155, 34, 35, 226, 227, 106, 107]}, u'Tutorial': {u'T8': 
[180, 60], u'T9': [181, 61], u'T6': [178, 58], u'T7': [179, 59], u'T4': [159, 39], u'T5': [160, 40], u'T2
': [157, 37], u'T3': [158, 38], u'T1': [130, 10], u'T14': [228, 108], u'T15': [229, 109], u'T10': [202, 8
2], u'T11': [203, 83], u'T12': [204, 84], u'T13': [205, 85]}}), ('CS1231', {u'Sectional Teaching': {u'1':
 [130, 10, 177, 178, 57, 58]}, u'Tutorial': {u'11': [228, 108], u'10': [227, 107], u'12': [229, 109], u'1
': [153, 33], u'3': [155, 35], u'2': [154, 34], u'5': [207, 87], u'4': [206, 86], u'7': [209, 89], u'6': 
[208, 88], u'9': [226, 106], u'8': [225, 105]}}), ('MA1101R', {u'Laboratory': {u'B01': [131], u'B03': [18
3], u'B02': [132], u'B05': [229], u'B04': [184], u'B07': [159], u'B06': [230], u'B08': [160]}, u'Tutorial
': {u'T11': [185, 65], u'T07': [205, 85], u'T06': [204, 84], u'T05': [203, 83], u'T04': [178, 58], u'T03'
: [177, 57], u'T02': [157, 37], u'T01': [156, 36], u'T10': [224, 104], u'T09': [226, 106], u'T08': [225, 
105]}, u'Lecture': {u'SL1': [136, 137, 16, 17, 208, 209, 88, 89]}}), ('CS2020', {u'Lecture': {u'1': [156,
 157, 36, 37, 226, 227, 106, 107]}, u'Recitation': {u'1': [229, 109], u'3': [231, 111], u'2': [230, 110]}
, u'Tutorial': {u'1': [178, 179, 58, 59], u'3': [158, 159, 38, 39], u'2': [182, 183, 62, 63], u'5': [202,
 203, 82, 83], u'4': [160, 161, 40, 41], u'6': [204, 205, 84, 85], u'9': [132, 133, 12, 13], u'8': [208, 
209, 88, 89]}}), ('CS1020', {u'Laboratory': {u'11': [208, 209, 88, 89], u'10': [208, 209, 88, 89], u'13':
 [202, 203, 82, 83], u'12': [204, 205, 84, 85], u'14': [208, 209, 88, 89], u'C01': [202, 203, 82, 83], u'
1': [202, 203, 82, 83], u'3': [206, 207, 86, 87], u'2': [204, 205, 84, 85], u'5': [202, 203, 82, 83], u'4
': [208, 209, 88, 89], u'7': [202, 203, 82, 83], u'6': [204, 205, 84, 85], u'9': [206, 207, 86, 87], u'8'
: [208, 209, 88, 89], u'C02': [204, 205, 84, 85], u'C03': [204, 205, 84, 85], u'C04': [206, 207, 86, 87],
 u'C05': [206, 207, 86, 87], u'C06': [206, 207, 86, 87]}, u'Sectional Teaching': {u'1': [154, 155, 34, 35
], u'2': [154, 155, 34, 35]}, u'Tutorial': {u'11': [229, 109], u'10': [228, 108], u'13': [177, 57], u'12'
: [230, 110], u'14': [181, 61], u'C01': [183, 63], u'1': [225, 105], u'3': [227, 107], u'2': [226, 106], 
u'5': [231, 111], u'4': [230, 110], u'7': [233, 113], u'6': [232, 112], u'9': [227, 107], u'8': [226, 106
], u'C02': [178, 58], u'C03': [180, 60], u'C04': [233, 113], u'C05': [227, 107], u'C06': [228, 108]}}), (
'CS2010', {u'Laboratory': {u'1': [130, 10], u'3': [132, 12], u'2': [131, 11], u'5': [134, 14], u'4': [133
, 13], u'7': [136, 16], u'6': [135, 15], u'8': [137, 17]}, u'Tutorial': {u'1': [177, 57], u'3': [179, 59]
, u'2': [178, 58], u'5': [182, 62], u'4': [180, 60], u'7': [179, 59], u'6': [183, 63], u'8': [180, 60]}, 
['ST2131_Lecture_SL1', 'ST2131_Tutorial_T1', 'MA1101R_Laboratory_B03', 'MA1101R_Tutorial_T06', 'MA1101R_L
ecture_SL1', 'CS1020_Laboratory_7', 'CS1020_Sectional Teaching_1', 'CS1020_Tutorial_14', 'CS2010_Laborato
ry_4', 'CS2010_Tutorial_8', 'CS2010_Lecture_1']
'''

# takes in a list of slots and returns lists of free days
def gotFreeDay(schedule):
    modCodes = Set([s.split('_')[0] for s in schedule])
    mods = [transformMod(query(m)) for m in modCodes]
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



testSchedule = ['ST2131_Lecture_SL1', 'ST2131_Tutorial_T1', 'MA1101R_Laboratory_B03', 'MA1101R_Tutorial_T06', 'MA1101R_Lecture_SL1', 'CS1020_Laboratory_7', 'CS1020_Sectional Teaching_1', 'CS1020_Tutorial_14', 'CS2010_Laboratory_4', 'CS2010_Tutorial_8', 'CS2010_Lecture_1']

print gotFreeDay(testSchedule)
