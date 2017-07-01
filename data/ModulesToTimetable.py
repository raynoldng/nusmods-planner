'''ModulesToTimetable.py
Prunes the original JSON file to contain only the timetable
'''

import json
from sets import Set
import sys

inputFile = sys.argv[1]

_mods = json.load(open(inputFile))
# dict maps module codes to list of lesson dicts
dict = {x['ModuleCode']: x['Timetable'] for x in _mods if 'Timetable' in x}

with open(inputFile[:inputFile.index('.json')] + '_timetable.json', 'w') as outfile:
    json.dump(dict, outfile)