'''queryParserBV.py 

Does the transformation of client query to SMTLIB2 input format and module
mapping required for client to construct timetable from SMT solving results
'''
from sets import Set
import json
from z3 import *
# from mod_utils import *
import random
from mod_utils import CalendarUtils
from mod_utils import *


def parseZ3Queryv4(numToTake, compmodsstr = [], optmodsstr = [], solver = Solver(),
                   options = {}):
    timetable = []
    selection = []

    if 'freeday' in options and options['freeday']:
        if 'possibleFreedays' in options:
            possibleFreedays = options['possibleFreedays']
        else:
            possibleFreedays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        compmodsstr.insert(0,ModWithFullDays(possibleFreedays))
        numToTake += 1

    # WARNING DEPRECATED
    if "numFreedays" in options and options["numFreedays"] > 0:
        numFreedays = options["numFreedays"]
        if "freedays" in options:
            freedays = options["freedays"]
        else:
            freedays = []
        compmodsstr.insert(0,freedayMod(numFreedays, freedays))
        numToTake += 1

    complen = len(compmodsstr)
    mods = compmodsstr + optmodsstr
    numMods = len(mods)

    X = [BitVec("x_%s" % i, 16) for i in range(numToTake)] # creates indicators
                                                           # determining which
                                                           # modules we try


    solver.add([X[i]==i for i in range(complen)])
    solver.add([X[i]<X[i+1] for i in range(numToTake-1)])
    solver.add(X[0] >= 0)
    solver.add(X[numToTake-1] < numMods)

    M = [BitVec("m_%s" % i, 16) for i in range(240)] # tells us which modules
                                                     # we are taking during
                                                     # each hour

    if "lockedLessonSlots" in options:
        lockedLessonsSlots = options['lockedLessonSlots']
        lockedLessonMapping = {l[:l.rindex('_')]: l  for l in lockedLessonsSlots}

    for modIndex, mod in enumerate(mods):
        moduleCode = mod[0]
        constraints = []
        selected = Or([X[i] == modIndex for i in range(numToTake)]) #is this mod selected

        for lessonType, slots in mod[1].iteritems():
            numSlots = len(slots)
            chosenSlot = BitVec('%s_%s' % (moduleCode, lessonType), 16)
            constraints.append(Implies(selected, And(chosenSlot >= 0, chosenSlot < numSlots)))
            # timetable += [Int('%s_%s_%s' % (moduleCode, lessonType, index))
            # for index in range(len(timing))]
            for slotIndex, (slotName, timing) in enumerate(slots):
                slotSelected = (chosenSlot == slotIndex)
                for index, time in enumerate(timing):
                    # implicants = [Int('%s_%s_%s' % (moduleCode, lessonType, index)) == time]
                    # implication = Implies(slotSelected, And(implicants))
                    # constraints.append(implication)

                    # replace modIndex with getVenueCode(slotName) when venue mapping is out
                    modLesson = modIndex * 10 + lessonTypeToCode(lessonType)
                    venueImplicant = Implies(slotSelected, M[time] == modLesson)
                    constraints.append(venueImplicant)

        solver.add(constraints)

    if "nobacktoback" in options and options["nobacktoback"]:
        for i in range(239):
            solver.add(Or(M[i] == -1, M[i+1] == -1, M[i] == M[i+1]))

    if 'lockedLessonSlots' in options:
        lockedSlots = options['lockedLessonSlots']
        for lessonSlot in lockedSlots:
           tokens = lessonSlot.split('_');
           moduleCode, lessonType, slot = tokens
           lessonSlots = filter(lambda x: x[0] == moduleCode, compmodsstr)[0][1][lessonType]
           lessonSlotIndex = [i for i, slotToTimes in enumerate(lessonSlots)
                              if slotToTimes[0] == slot][0]
           solver.add(BitVec('%s_%s' % (moduleCode, lessonType), 16) == lessonSlotIndex)

    '''
    To implement no lesson before/after, we assign a new dummy mod with index
    numToTake and assert the implicants
    '''
    if "noLessonsBefore" in options:
        hours = hoursBefore(options['noLessonsBefore'])
        for i in hours:
            solver.add(M[i] == 999)

    if "noLessonsAfter" in options:
        hours = hoursAfter(options['noLessonsAfter'])
        for i in hours:
            solver.add(M[i] == 999)



def toSMT2Benchmark(f, status="unknown", name="benchmark", logic="QF_BV"):
    v = (Ast * 0)()
    if isinstance(f, Solver):
        a = f.assertions()
    if len(a) == 0:
        f = BoolVal(True)
    else:
        f = And(*a)
    return Z3_benchmark_to_smtlib_string(f.ctx_ref(), name, logic,
                                         status, "", 0, v, f.as_ast())

def parseQuery(numToTake, compmodsstr = [], optmodsstr = [], options = {}, semester = 'AY1617S2',
    debug = False):
    s = Solver()
    modUtils = CalendarUtils(semester)

    compmods = [transformMod(modUtils.query(m)) for m in compmodsstr]
    optmods = [transformMod(modUtils.query(m)) for m in optmodsstr]
    # transfomrs slotname to timing mappings into list of tuples (s,t) instead
    complst = [[i[0], {k:v.items() for k,v in i[1].items()}] for i in compmods]
    optlst = [[i[0], {k:v.items() for k,v in i[1].items()}] for i in optmods]
    parseZ3Queryv4(numToTake, complst, optlst, s, options)
    modlst = complst + optlst
    # return toSMT2Benchmark(s)
    if debug:
        return [s, modlst]
    else:
        return [toSMT2Benchmark(s), modsListToLessonMapping(compmods + optmods)]
