'''
Convenience scripts to pull relevent data from json files
Called scripts.py for lack of a better word
'''

import json
from sets import Set

_mods = json.load(open('timetable.json'))
# dict maps module codes to list of lesson dicts
dict = {x['ModuleCode']: x['Timetable'] for x in _mods if 'Timetable' in x}

''' scripts.py
Convenience scripts to generate the json files required for NUSMods Planner

Usage:
python scripts.py

Warning! Will overwrite existing data
'''
def pullLessonTypes():
    allLessons = [dict[k] for k in dict.keys()]
    allLessons = [i for sublist in allLessons for i in sublist]
    lessonTypes = Set([l['LessonType'] for l in allLessons])
    lessonTypes = list(lessonTypes)
    lessonTypes.sort()
    return lessonTypes

def pullVenues():
    allLessons = [dict[k] for k in dict.keys()]
    allLessons = [i for sublist in allLessons for i in sublist]
    venues = Set([l['Venue'] for l in allLessons])
    venues = list(venues)
    venues.sort()
    return venues

def venueMap(str):
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
        return 5

def venueMapping(venueFilePath):
    """Creates a dict mapping venues to an ID, currently the IDs are:
    0:science, 1:Computing/Business, 2: Engineering, 4: everything else

    :param venueFilePath: path to txt of venues in list form
    :returns: mapping of venues to IDs
    :rtype: dictionary
    """
    venues = open(venueFilePath).readlines();
    venueMapping = {}
    for v in venues:
        venueMapping[v] = venueMap(v)
    return venueMapping

# Copied from mod_utils.py
# returns a dictionary mapping venues to their cluster - 0: Science, 1:
# Computing/Business/I3, 2: Engineering, 3: Arts, 4: manual updating is
# possible intending to slowly update m_dict here using if else and prefix
# matching, then commenting it out so the process is faster
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

def run():
    # generate the list of venues, venues.txt
    # f = open('venues.txt', 'w')
    # f.writelines(pullVenues)

    # generate mapping of venues to IDS, venuecodes.json
    json.dump(venueMapping('venues.txt'), open('venuecodes.json', 'w'))

run()
