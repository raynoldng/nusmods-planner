import requests
from sets import Set
import json
from z3 import *

ENV = "DEV" # faster to do everything offline


## Helper functions
if ENV == "DEV":
    _mods = json.load(open('timetable.json'))
    _dict = {x['ModuleCode']: x['Timetable'] for x in _mods if 'Timetable' in x}

# modjson: json object
def splitIntoLessonTypes(modjson):
    mod = modjson['Timetable']
    lessonTypes = Set([i['LessonType'] for i in mod])
    lessons = [list(filter(lambda x: x['LessonType'] == lesson, mod)) for lesson in lessonTypes]
    return lessons

def queryNUSMODS(code):
    # if in DEV mode then pull everything from local sources
    if ENV == "DEV":
        return _dict[code]
    else:
        r = requests.get('http://api.nusmods.com/2014-2015/2/modules/' +  code + '.json')
        r = r.json()
        return r

# print cs1010
# print cs1010['LessonType']
# lessonType = Set([i for i in cs1010['LessonType']])

# def printJSON(obj):
#    print json.dumps(obj, indent=4, sort_keys=True)

# print splitIntoLessonTypes(json.load(open('cs1010.json')))

## Testing the queryNUSMODS local calls
print queryNUSMODS('CS1010')
