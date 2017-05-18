# going to import data from ../data/venuecodes.json eventually, for now we assume different mods = different venues,
# same mod = same venue - implmenetation will not change much; instead of mapping to module number, we map to venuecode instead

from z3 import *
from mod_utils import *

def freeDay(x):
	day = range(x*24,(x+1)*24)
	return day + [i+120 for i in day]

# stable
def parseZ3Queryv2(compmods, optmods, numToTake, solver = Solver()):
    complen = len(compmods)
    if complen > numToTake:
    	dummy = Int('dummy')
    	solver.add([dummy<1,dummy>1]) #for unsat
    	return
    timetable = []
    selection = []
    mods = compmods + optmods
    numMods = len(mods)
    X = [Int("x_%s" % i) for i in range(numToTake)] # creates indicators determining which modules we try
    solver.add([X[i]==i for i in range(complen)])
    solver.add([X[i]<X[i+1] for i in range(numToTake-1)])
    solver.add(X[0] >= 0)
    solver.add(X[numToTake-1] < numMods)
    for modIndex, mod in enumerate(mods):
        moduleCode = mod[0]
        constraints = []
        selected = Or([X[i] == modIndex for i in range(numToTake)]) #is this mod selected
        for lessonType, slots in mod[1].iteritems():
            firstFlag = True
            slotSelectors = []
            for slotName, timing in slots.iteritems():
                if firstFlag:
                    # add to timetable
                    timetable += [Int('%s_%s_%s' % (moduleCode, lessonType, index))
                                  for index in range(len(timing))]
                    firstFlag = False
                selector = Bool('%s_%s_%s' % (moduleCode, lessonType[:3], slotName))
                constraints.append(Implies(selector,Or([modIndex == X[i] for i in range(numToTake)]))) 
                #small bug fix here to guarantee selector can only be true when we are taking that mod, otherwise solver could randomly fill up free slot
                selection.append(selector)
                slotSelectors.append(selector)
                for index, time in enumerate(timing):
                    implicants = [Int('%s_%s_%s' % (moduleCode, lessonType, index)) == time]
                    implication = Implies(selector, And(implicants))
                    constraints.append(implication)
            constraints.append(Or(Or(slotSelectors),Not(selected))) 
        # not selected then we don't care, tutorial for a mod we don't choose can be at -1945024 hrs
        # solver.add(Implies(selected, constraints))
        solver.add(constraints)
    # print timetable
    # want timetable to be distinct
    solver.add(Or([Distinct(timetable+freeDay(i)) for i in range(5)]))
    return selection

# stable
def timetablePlannerv2(compmodsstr, optmodsstr, numToTake):
    s = Solver()
    compmods = [transformMod(query(m)) for m in compmodsstr]
    optmods = [transformMod(query(m)) for m in optmodsstr]
    selection = parseZ3Queryv2(compmods, optmods, numToTake, s)
    if s.check() == sat:
        print "Candidate:"
        m = s.model()
        # print m
        for s in selection:
            if m[s]:
                print s
    else:
        print "free day not possible"


def minTravelQueryv3(compmodsstr, optmodsstr, numToTake):
    for i in range(10):
        s = Solver()
        compmods = [transformMod(query(m)) for m in compmodsstr]
        optmods = [transformMod(query(m)) for m in optmodsstr]
        selection = parseZ3Queryv3(compmods, optmods, numToTake, s, "mintravel", i)
        if s.check() == sat:
            print "Candidate:"
            m = s.model()
            # print m
            for s in selection:
                if m[s]:
                    print s
            print "travel time: " + str(i)
            break
        else:
            print "unsat" + str(i)

def timetablePlannerv3(compmodsstr, optmodsstr, numToTake):
    s = Solver()
    compmods = [transformMod(query(m)) for m in compmodsstr]
    optmods = [transformMod(query(m)) for m in optmodsstr]
    selection = parseZ3Queryv3(compmods, optmods, numToTake, s)
    if s.check() == sat:
        print "Candidate:"
        m = s.model()
        # print m
        for s in selection:
            if m[s]:
                print s
    else:
        print "free day not possible"

# including option, which can be set to freday or mintravel for now
def parseZ3Queryv3(compmods, optmods, numToTake, solver, option = "freeday", backtoback = 0):
    complen = len(compmods)
    if complen > numToTake:
        dummy = Int('dummy')
        solver.add([dummy<1,dummy>1]) #for unsat
        return
    timetable = []
    selection = []
    mods = compmods + optmods
    numMods = len(mods)


    X = [Int("x_%s" % i) for i in range(numToTake)] # creates indicators determining which modules we try
    solver.add([X[i]==i for i in range(complen)])
    solver.add([X[i]<X[i+1] for i in range(numToTake-1)])
    solver.add(X[0] >= 0)
    solver.add(X[numToTake-1] < numMods)

    M = [Int("m_%s" % i) for i in range(240)] # tells us which modules we are taking during each hour
    if (option == "mintravel"):
        Costs = [Int("cost_%s" % i) for i in range(239)]
        for i in range(239):
            solver.add(Costs[i] == If(Or(M[i] == -1, M[i+1] == -1, M[i] == M[i+1]), 0, 1))
            solver.add(Sum(Costs) == backtoback)

    for modIndex, mod in enumerate(mods):
        moduleCode = mod[0]
        constraints = []
        selected = Or([X[i] == modIndex for i in range(numToTake)]) #is this mod selected
        for lessonType, slots in mod[1].iteritems():
            firstFlag = True
            slotSelectors = []
            for slotName, timing in slots.iteritems():
                if firstFlag:
                    # add to timetable
                    timetable += [Int('%s_%s_%s' % (moduleCode, lessonType, index))
                                  for index in range(len(timing))]
                    firstFlag = False
                selector = Bool('%s_%s_%s' % (moduleCode, lessonType[:3], slotName))
                constraints.append(Implies(selector,Or([modIndex == X[i] for i in range(numToTake)]))) 
                #small bug fix here to guarantee selector can only be true when we are taking that mod, otherwise solver could randomly fill up free slot

                selection.append(selector)
                slotSelectors.append(selector)
                for index, time in enumerate(timing):
                    implicants = [Int('%s_%s_%s' % (moduleCode, lessonType, index)) == time]
                    implication = Implies(selector, And(implicants))
                    constraints.append(implication)

                    venueImplicant = Implies(selector, M[time] == modIndex) # replace modIndex with getVenueCode(slotName) when venue mapping is out
                    constraints.append(venueImplicant)

            constraints.append(Or(Or(slotSelectors),Not(selected))) 
        # not selected then we don't care, tutorial for a mod we don't choose can be at -1945024 hrs
        # solver.add(Implies(selected, constraints)

        solver.add(constraints)

    if (option == "freeday"): 
        freeDayConstraint = [Or([And([M[i] == -1 for i in freeDay(j)]) for j in range(5)])]
        # solver.add(Or([Distinct(timetable+freeDay(i)) for i in range(5)]))
        solver.add(freeDayConstraint)

    # print timetable
    # want timetable to be distinct
    return selection