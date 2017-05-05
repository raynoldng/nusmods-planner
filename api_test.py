import requests
from sets import Set
import json
from z3 import *


## Helper functions

# modjson: json object
def splitIntoLessonTypes(modjson):
    mod = modjson['Timetable']
    lessonTypes = Set([i['LessonType'] for i in mod])
    lessons = [list(filter(lambda x: x['LessonType'] == lesson, mod)) for lesson in lessonTypes]
    return lessons

def queryNUSMODS(code):
    r = requests.get('http://api.nusmods.com/2014-2015/2/modules/' +  code + '.json')
    r = r.json()
    return r

# print cs1010
# print cs1010['LessonType']
# lessonType = Set([i for i in cs1010['LessonType']])

def printJSON(obj):
    print json.dumps(obj, indent=4, sort_keys=True)

print splitIntoLessonTypes(json.load(open('cs1010.json')))
