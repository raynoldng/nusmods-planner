import requests
from sets import Set
import json
from z3 import *


## Helper functions

# modjson: json object
def splitIntoLessonTypes(mod):
    #mod = modjson['Timetable']
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
def query(code):
	r = requests.get('http://api.nusmods.com/2016-2017/1/modules/' + code.upper() + '/timetable.json')
	r = r.json()
	return r

#some hard code
weekdays = {"Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3, "Friday": 4}

# returns list of discrete timeslots based on hour-based indexing in a fortnight
# used for z3's distinct query. 0-119 first week, 120-239 second week.
def timeList(weektext, daytext, starttime, endtime):
	ofst = weekdays[daytext]*24
	lst = [i+ofst for i in range(int(starttime)/100, int(endtime)/100)]
	if (weektext == "Odd Week"):
		return lst
	elif (weektext == "Even Week"):
		return [i+120 for i in lst]
	# default every week
	else:
		return [i+120 for i in lst]+lst



# print cs1010
# print cs1010['LessonType']
# lessonType = Set([i for i in cs1010['LessonType']])

def printJSON(obj):
    print json.dumps(obj, indent=4, sort_keys=True)

f = open('out.txt', 'w')

print >> f, splitIntoLessonTypes(json.load(open('st2131.json')))

f2 = open('out2.txt', 'w')
print >> f2, splitIntoLessonTypes(query('st2131'))
f2.close()

f.close()
