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

numDays = 10
FREEDAY_OFFSET = 1000 # required to resolve noLessonsBefore/After conflict

def parseZ3Queryv4(numToTake, compMods = [], optMods = [], solver = Solver(),
                   options = {}, semester = 'AY1617S2'):
    modUtils = CalendarUtils(semester)

    timetable = []
    selection = []

    compModsMapping = [transformMod(modUtils.query(m)) for m in compMods]
    compModsMapping = [[i[0], {k:v.items() for k,v in i[1].items()}] for i in compModsMapping]

    optModsMapping = [transformMod(modUtils.query(m)) for m in optMods]
    optModsMapping = [[i[0], {k:v.items() for k,v in i[1].items()}] for i in optModsMapping]

    # TODO migrate logic to function
    if 'freeday' in options and options['freeday']:
        if 'possibleFreedays' in options and len(options['possibleFreedays']) > 0:
            possibleFreedays = options['possibleFreedays']
        else:
            possibleFreedays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        compModsMapping.insert(0, ModWithFullDays(possibleFreedays))
        numToTake += 1

    # WARNING DEPRECATED
    if "numFreedays" in options and options["numFreedays"] > 0:
        numFreedays = options["numFreedays"]
        if "freedays" in options:
            freedays = options["freedays"]
        else:
            freedays = []
        compModsMapping.insert(0,freedayMod(numFreedays, freedays))
        numToTake += 1

    numCompMods = len(compModsMapping)
    modsMapping = compModsMapping + optModsMapping
    numMods = len(modsMapping)

    X = [BitVec("x_%s" % i, 16) for i in range(numToTake)] # creates indicators
                                                           # determining which
                                                           # modules we try


    solver.add([X[i]==i for i in range(numCompMods)])
    solver.add([X[i]<X[i+1] for i in range(numToTake-1)])
    solver.add(X[0] >= 0)
    solver.add(X[numToTake-1] < numMods)

    M = [BitVec("m_%s" % i, 16) for i in range(240)] # tells us which modules
                                                     # we are taking during
                                                     # each hour

    for modIndex, mod in enumerate(modsMapping):
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

                    # need to consider the special case where its a freeday
                    # it follows that FREEDAY mods have a venue code of > 1000
                    if 'FREEDAY' in moduleCode:
                        modLesson = 1000 + 10 * modIndex + lessonTypeToCode(lessonType)
                    else:
                        modLesson = modIndex * 10 + lessonTypeToCode(lessonType)
                    venueImplicant = Implies(slotSelected, M[time] == modLesson)
                    constraints.append(venueImplicant)

        solver.add(constraints)

    # add all of the option related constraints
    if 'lockedLessonSlots' in options:
        addLockedLessons(solver, modsMapping, options['lockedLessonSlots'], compMods)
    if 'noLessonsBefore' in options:
        addNoLessonsBefore(solver, options['noLessonsBefore'], M)
    if 'noLessonsAfter' in options:
        addNoLessonsBefore(solver, options['noLessonsAfter'], M)
    if 'lunchBreak' in options and options['lunchBreak']:
        addLunchBreak(solver, M)

    return [solver, modsMapping]


def addLockedLessons(solver, modMapping, lockedLessonSlots, compMods):
    # additional check, locked lessons might be artifacts from client side
    lockedLessonSlots = [slot for slot in lockedLessonSlots if slot.split('_')[0] in compMods]

    for lessonSlot in lockedLessonSlots:
        # for each locked lesson slot, find its corresponding slot index in the modsMapping
        # and assert that modules_lesson variable is that index
        tokens = lessonSlot.split('_');
        moduleCode, lessonType, slot = tokens

        lessonSlots = filter(lambda modMap: modMap[0] == moduleCode, modMapping)
        assert len(lessonSlots) == 1
        lessonSlots = lessonSlots[0][1][lessonType]

        slotIndex = [i for i, slotToHours in enumerate(lessonSlots) if slotToHours[0] == slot]
        assert len(slotIndex) == 1
        slotIndex = slotIndex[0]

        solver.add(BitVec('%s_%s' % (moduleCode, lessonType), 16) == slotIndex)

def addNoLessonsBefore(solver, time, M):
    hours = hoursBefore(time)
    for i in hours:
        solver.add(M[i] >= FREEDAY_OFFSET)

def addNoLessonsAfter(solver, time, M):
    hours = hoursAfter(time)
    for i in hours:
        solver.add(M[i] >= FREEDAY_OFFSET)

def addLunchBreak(solver, M):
    for i in range(numDays):
        solver.add(Or([M[24*i + h] >= FREEDAY_OFFSET for h in LUNCH_HOURS]))


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

def parseQuery(numToTake, compMods = [], optMods = [], options = {}, semester = 'AY1617S2',
    debug = False):

    solver, modsMapping = parseZ3Queryv4(numToTake, compMods, optMods, Solver(), options, semester)

    if debug:
        return [solver, modsMapping]
    else:
        modLessonMapping = [[i[0], {k: [j[0] for j in v] for k, v in i[1].iteritems()}] for i in modsMapping]
        return [toSMT2Benchmark(solver), modLessonMapping]
