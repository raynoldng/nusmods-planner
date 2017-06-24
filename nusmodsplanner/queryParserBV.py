'''queryParserBV.py 

Does the transformation of client query to SMTLIB2 input format and module
mapping required for client to construct timetable from SMT solving results
'''
from sets import Set
import json
from z3 import *
from mod_utils import *

def parseZ3Queryv4(numToTake, compmodsstr = [], optmodsstr = [], solver = Solver(),
                   options = {}):
    complen = len(compmodsstr)
    if complen > numToTake:
        dummy = BitVec('dummy', 16)
        solver.add([dummy<1,dummy>1]) #for unsat
        return
    timetable = []
    selection = []
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

    if "freeday" in options and options["freeday"]:
        freeDayConstraint = [Or([And([M[i] == -1 for i in freeDay(j)]) for j in range(5)])]
        # solver.add(Or([Distinct(timetable+freeDay(i)) for i in range(5)]))
        solver.add(freeDayConstraint)

    if "nobacktoback" in options and options["nobacktoback"]:
        for i in range(239):
            solver.add(Or(M[i] == -1, M[i+1] == -1, M[i] == M[i+1]))

    '''
    To implement no lesson before/after, we assign a new dummy mod with index
    numToTake and assert the implicants
    '''
    if "nolessonsbefore" in options:
        hours = hoursBefore(options['nolessonsbefore'])
        for i in hours:
            solver.add(M[i] == 999)

    if "nolessonsafter" in options:
        hours = hoursAfter(options['nolessonsafter'])
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

def parseQuery(numToTake, compmodsstr = [], optmodsstr = [], options = {},
    debug = False):
    s = Solver()
    compmods = [transformMod(query(m)) for m in compmodsstr]
    optmods = [transformMod(query(m)) for m in optmodsstr]
    # transfomrs slotname to timing mappings into list of tuples (s,t) instead
    complst = [[i[0], {k:v.items() for k,v in i[1].items()}] for i in compmods]
    optlst = [[i[0], {k:v.items() for k,v in i[1].items()}] for i in optmods]
    modlst = complst + optlst
    parseZ3Queryv4(numToTake, complst, optlst, s, options)
    # return toSMT2Benchmark(s)
    if debug:
        return [s, modlst]
    else:
        return [toSMT2Benchmark(s), modsListToLessonMapping(compmods + optmods)]