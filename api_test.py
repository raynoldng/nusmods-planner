import requests
from sets import Set
import json
from z3 import *


## Helper functions

# mod: json object
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
def modQuery(code):
	r = requests.get('http://api.nusmods.com/2016-2017/2/modules/' + code.upper() + '/timetable.json')
	r = r.json()
	return r

# returns free day constraint, x is a weekday
def freeDay(x):
	num = weekdays[x]
	day = range(num*24,(num+1)*24)
	return day + [i+120 for i in day]

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

# user input: list of potential modules he wishes to take
def getModel(modList, numToTake): # say a person provides a list of 8 modules he could take next sem, and wants to choose 5
	numMods = len(modList)
	X = [Int("x_%s" % i) for i in range(numToTake)] # creates 5 indicators determining which modules we try
	constr_1 = [Distinct(X)] 
	constr_2 = [And(X[i] >= 0, X[i]<numMods) for i in range(numToTake)]
	modList = [i.upper() for i in modList]
	data = [splitIntoLessonTypes(modQuery(i)) for i in modList]
	x4 = [Int("x4_%s" % i) for i in range(X[0])]
	s = Solver()
	s.add(constr_1+constr_2)
	print s.check()
	print s.model()

# print cs1010
# print cs1010['LessonType']
# lessonType = Set([i for i in cs1010['LessonType']])

def printJSON(obj):
    print json.dumps(obj, indent=4, sort_keys=True)

f = open('out.txt', 'w')

print >> f, splitIntoLessonTypes(json.load(open('st2131.json')))

f2 = open('out2.txt', 'w')
print >> f2, splitIntoLessonTypes(modQuery('st2131'))
f2.close()

f.close()

getModel(['st2131','ma2108s','geh1036','cs2100','ma2101s','cs2020','geq1000','sp1541'], 5)