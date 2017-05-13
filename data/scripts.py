'''
Convenience scripts to pull relevent data from json files
Called scripts.py for lack of a better word
'''

import json
from sets import Set

_mods = json.load(open('timetable.json'))
# dict maps module codes to list of lesson dicts
dict = {x['ModuleCode']: x['Timetable'] for x in _mods if 'Timetable' in x}

def pullVenues():
    allLessons = [dict[k] for k in dict.keys()]
    allLessons = [i for sublist in allLessons for i in sublist]
    venues = Set([l['Venue'] for l in allLessons])
    venues = list(venues)
    venues.sort()
    for v in venues:
        print v

pullVenues()
