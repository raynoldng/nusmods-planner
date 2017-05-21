# going to import data from ../data/venuecodes.json eventually, for now we assume different mods = different venues,
# same mod = same venue - implmenetation will not change much; instead of mapping to module number, we map to venuecode instead

# all functions here are outdated, used for testing comparison only

from z3 import *
from mod_utils import *

def freeDay(x):
	day = range(x*24,(x+1)*24)
	return day + [i+120 for i in day]

# stable
def parseZ3Queryv2(numToTake, compmods = [], optmods = [], solver = Solver()):
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
def timetablePlannerv2(numToTake, compmodsstr = [], optmodsstr = []):
    s = Solver()
    compmods = [transformMod(query(m)) for m in compmodsstr]
    optmods = [transformMod(query(m)) for m in optmodsstr]
    selection = parseZ3Queryv2(numToTake, compmods, optmods, s)
    if s.check() == sat:
        print "Candidate:"
        m = s.model()
        # print m
        for s in selection:
            if m[s]:
                print s
    else:
        print "free day not possible"


def minTravelQueryv3(numToTake, compmodsstr = [], optmodsstr = []):
    for i in range(10):
        s = Solver()
        compmods = [transformMod(query(m)) for m in compmodsstr]
        optmods = [transformMod(query(m)) for m in optmodsstr]
        selection = parseZ3Queryv3(numToTake, compmods, optmods, s, "mintravel", i)
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

def noBacktoBackQueryv3(numToTake, compmodsstr = [], optmodsstr = []):
    s = Solver()
    compmods = [transformMod(query(m)) for m in compmodsstr]
    optmods = [transformMod(query(m)) for m in optmodsstr]
    selection = parseZ3Queryv3(numToTake, compmods, optmods, s, "nobacktoback")
    if s.check() == sat:
        print "Candidate:"
        m = s.model()
        # print m
        for s in selection:
            if m[s]:
                print s
    else:
        print "not possible"

def timetablePlannerv3(numToTake, compmodsstr = [], optmodsstr = []):
    s = Solver()
    compmods = [transformMod(query(m)) for m in compmodsstr]
    optmods = [transformMod(query(m)) for m in optmodsstr]
    selection = parseZ3Queryv3(numToTake, compmods, optmods, s)
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
def parseZ3Queryv3(numToTake, compmodsstr = [], optmodsstr = [], solver = Solver(),
                   option = "freeday", backtoback = 0):
    complen = len(compmodsstr)
    if complen > numToTake:
        dummy = Int('dummy')
        solver.add([dummy<1,dummy>1]) #for unsat
        return
    timetable = []
    selection = []
    mods = compmodsstr + optmodsstr
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

                    # replace modIndex with getVenueCode(slotName) when venue mapping is out
                    venueImplicant = Implies(selector, M[time] == modIndex)
                    constraints.append(venueImplicant)

            constraints.append(Or(Or(slotSelectors),Not(selected)))
        # not selected then we don't care, tutorial for a mod we don't choose can be at -1945024 hrs
        # solver.add(Implies(selected, constraints)

        solver.add(constraints)

    if (option == "freeday"):
        freeDayConstraint = [Or([And([M[i] == -1 for i in freeDay(j)]) for j in range(5)])]
        # solver.add(Or([Distinct(timetable+freeDay(i)) for i in range(5)]))
        solver.add(freeDayConstraint)

    if (option == "nobacktoback"):
        for i in range(239):
            solver.add(Or(M[i] == -1, M[i+1] == -1, M[i] == M[i+1]))

    # print timetable
    # want timetable to be distinct
    return selection


# overhaul of query method
def parseZ3Queryv4(numToTake, compmodsstr = [], optmodsstr = [], solver = Solver(),
                   option = "freeday", backtoback = 0):
    complen = len(compmodsstr)
    if complen > numToTake:
        dummy = Int('dummy')
        solver.add([dummy<1,dummy>1]) #for unsat
        return
    timetable = []
    selection = []
    mods = compmodsstr + optmodsstr
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
            numSlots = len(slots)
            chosenSlot = Int('%s_%s' % (moduleCode, lessonType[:3]))
            constraints.append(Implies(selected, And(chosenSlot >= 0, chosenSlot < numSlots)))
            # timetable += [Int('%s_%s_%s' % (moduleCode, lessonType, index)) for index in range(len(timing))]
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

# option can be freeday or nobacktoback
def generalQueryv4(numToTake, compmodsstr = [], optmodsstr = [], option = "freeday"):
    s = Solver()
    compmods = [transformMod(query(m)) for m in compmodsstr]
    optmods = [transformMod(query(m)) for m in optmodsstr]
    # transfomrs slotname to timing mappings into list of tuples (s,t) instead
    complst = [[i[0], {k:v.items() for k,v in i[1].items()}] for i in compmods]
    optlst = [[i[0], {k:v.items() for k,v in i[1].items()}] for i in optmods]
    modlst = complst + optlst
    parseZ3Queryv4(numToTake, complst, optlst, s, option, backtoback)
    if s.check() == sat:
        print "Candidate:"
        m = s.model()
        outputFormatter(m, numToTake, modlst)
    else:
        print "free day not possible"