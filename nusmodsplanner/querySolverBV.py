'''querySolver.py

ONLY USED IN TESTING!

The actual solving is done on the cliet side to performance concerns. This
helper script is for validating the correctness of SMTLIB2 syntax generated
'''
from sets import Set
import json
from z3 import *
from mod_utils import *
from queryParserBV import parseQuery

# Main function 
def solveQuery(numToTake, compmodsstr = [], optmodsstr = [], options = {}, semester = 'AY1617S2'):
    s, modlst = parseQuery(numToTake, compmodsstr, optmodsstr, options, semester,
                           debug = True)
    if s.check() == sat:
        # print "Candidate Timetable:"
        m = s.model()
        # outputFormatter(m, numToTake, modlst)
        return timetable(m, numToTake, modlst)
    else:
        return []

def timetablePlannerv4(numToTake, compmodsstr = [], optmodsstr = []):
    s = Solver()
    compmods = [transformMod(query(m)) for m in compmodsstr]
    optmods = [transformMod(query(m)) for m in optmodsstr]
    # transfomrs slotname to timing mappings into list of tuples (s,t) instead
    complst = [[i[0], {k:v.items() for k,v in i[1].items()}] for i in compmods]
    optlst = [[i[0], {k:v.items() for k,v in i[1].items()}] for i in optmods]
    modlst = complst + optlst
    parseZ3Queryv4(numToTake, complst, optlst, s)
    if s.check() == sat:
        print "Candidate:"
        m = s.model()
        outputFormatter(m, numToTake, modlst)
    else:
        print "free day not possible"

def timetable(model, numToTake, modlst):
    result = []
    for i in range(numToTake):
        modIndex = model[BitVec("x_%s" % i, 16)].as_long()
        mod = modlst[modIndex]
        moduleCode = mod[0]
        # print "Module: %s" % moduleCode
        for lessonType, slots in mod[1].iteritems():
            # print "All lesson slots: %s" % slots
            chosenSlot = model[BitVec('%s_%s' % (moduleCode, lessonType), 16)].as_long()
            # print "module code: %s, lesson: %s, model: %s" % (moduleCode, lessonType, chosenSlot)
            slotName = slots[chosenSlot][0]
            result.append("%s_%s_%s" % (moduleCode, lessonType, slotName))
    return result

# def outputFormatter(model, numToTake, modlst):
#     for i in range(numToTake):
#         modIndex = model[BitVec("x_%s" % i, 16)].as_long()
#         mod = modlst[modIndex]
#         moduleCode = mod[0]
#         # print "Module: %s" % moduleCode
#         for lessonType, slots in mod[1].iteritems():
#             # print "All lesson slots: %s" % slots
#             chosenSlot = model[BitVec('%s_%s' % (moduleCode, lessonType), 16)].as_long()
#             # print "module code: %s, lesson: %s, model: %s" % (moduleCode, lessonType, chosenSlot)
#             slotName = slots[chosenSlot][0]
#             print "%s_%s_%s" % (moduleCode, lessonType, slotName)

def generalQueryv4(numToTake, compmodsstr = [], optmodsstr = [], option = "freeday"):
    s = Solver()
    compmods = [transformMod(query(m)) for m in compmodsstr]
    optmods = [transformMod(query(m)) for m in optmodsstr]
    
    
    # transfomrs slotname to timing mappings into list of tuples (s,t) instead
    complst = [[i[0], {k:v.items() for k,v in i[1].items()}] for i in compmods]
    optlst = [[i[0], {k:v.items() for k,v in i[1].items()}] for i in optmods]
    modlst = complst + optlst
    # print modlst

    # prepare list of mod -> lessons -> slots
    opt = {i[0]: {k:v.keys() for k, v in i[1].items()} for i in optmods}
    comp = {i[0]: {k:v.keys() for k, v in i[1].items()} for i in compmods}
    modMappings = opt.copy()
    modMappings.update(comp)
    print modMappings

    parseZ3Queryv4(numToTake, complst, optlst, s, option)
    if s.check() == sat:
        print "Candidate:"
        m = s.model()
        outputFormatter(m, numToTake, modlst)
    else:
        print "free day not possible"
    # print out the smtlib2 syntax of query
    # print "Here is the output"
    # print toSMT2Benchmark(s)


'''
s = parseQuery(4, [], ['cs1010', 'st2131', 'cs1231', 'ma1101r','cs2020',
                                'cs2010', 'ma2108'], "freeday")
'''

# s = generalQueryv4(4, [], ["CS1020", "CS1231", "CS2020", "CS2100", "CS2105", "MA1101R", "ST2131"], "freeday")
