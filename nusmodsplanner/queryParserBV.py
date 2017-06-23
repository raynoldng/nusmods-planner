from sets import Set
import json
from z3 import *
from mod_utils import *

def freeDay(x):
    day = range(x*24,(x+1)*24)
    return day + [i+120 for i in day]
# returns selection: list of all lesson slots for us to iterate through the model to find schedule

def parseZ3Queryv4(numToTake, compmodsstr = [], optmodsstr = [], solver = Solver(),
                   option = "freeday", backtoback = 0):
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
    if (option == "mintravel"):
        Costs = [BitVec("cost_%s" % i, 16) for i in range(239)]
        for i in range(239):
            solver.add(Costs[i] == If(Or(M[i] == -1, M[i+1] == -1, M[i] == M[i+1]), 0, 1))
            solver.add(Sum(Costs) == backtoback)

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
                    venueImplicant = Implies(slotSelected, M[time] == modIndex)
                    constraints.append(venueImplicant)

        solver.add(constraints)

    if (option == "freeday"):
        freeDayConstraint = [Or([And([M[i] == -1 for i in freeDay(j)]) for j in range(5)])]
        # solver.add(Or([Distinct(timetable+freeDay(i)) for i in range(5)]))
        solver.add(freeDayConstraint)

    if (option == "nobacktoback"):
        for i in range(239):
            solver.add(Or(M[i] == -1, M[i+1] == -1, M[i] == M[i+1]))


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

def parseQuery(numToTake, compmodsstr = [], optmodsstr = [], option = "freeday"):
    s = Solver()
    compmods = [transformMod(query(m)) for m in compmodsstr]
    optmods = [transformMod(query(m)) for m in optmodsstr]
    # transfomrs slotname to timing mappings into list of tuples (s,t) instead
    complst = [[i[0], {k:v.items() for k,v in i[1].items()}] for i in compmods]
    optlst = [[i[0], {k:v.items() for k,v in i[1].items()}] for i in optmods]
    modlst = complst + optlst
    parseZ3Queryv4(numToTake, complst, optlst, s, option)
    # return toSMT2Benchmark(s)
    return [toSMT2Benchmark(s), modsListToLessonMapping(compmods + optmods)]