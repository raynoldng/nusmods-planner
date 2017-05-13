'''
Attempt to model travelling

Problem Statement
-----------------

There are 3 locations = {a,b,c} and the distances between nodes are:
- a <-> b: 10
- a <-> c: 2
- b <-> c: 5

There are 5 time slots. At the start of every time slot we can either:
1. stay where we are, 0 cost
2, most to another node, cost as stated above

Goal: to visit all nodes with minimum cost

Example optimmal solution: [a,a,c,c,b], cost of 7

Representation
--------------
The locations are 0-indexed.

'''
from z3 import *

time = 5 # number of time steps

solver = Optimize()
costs = [Int("cost_%s" % i) for i in range(time)]
locations = [Int("loc_%s" % i) for i in range(time)]

# constrain locations
location_constriants = And([Or([loc == i for i in [0,1,2]]) for loc in locations])
solver.add(location_constriants)

# add visit all locations constraint
solver.add(And([Or([l == node for l in locations]) for node in [0,1,2]]))

# model travelling costs
solver.add(costs[0] == 0) # initliaze initial cost to 0
for i in range(1,time):
    prevLoc = locations[i - 1]
    currLoc = locations[i]
    prevCost = costs[i -1]
    currCost = costs[i]
    implications = [
        Implies(prevLoc == currLoc, currCost == prevCost),
        Implies(And(Or(prevLoc == 0, currLoc  == 0), Or(prevLoc == 1, currLoc  == 1)),
                currCost == prevCost + 10),
        Implies(And(Or(prevLoc == 0, currLoc  == 0), Or(prevLoc == 2, currLoc  == 2)),
                currCost == prevCost + 2),
        Implies(And(Or(prevLoc == 1, currLoc  == 1), Or(prevLoc == 2, currLoc  == 2)),
                currCost == prevCost + 5)
    ]
    solver.add(implications)

# minimize cost
goal = solver.minimize(costs[-1])

print solver.check()

# print out model

m = solver.model()
for l in locations:
    print m[l]
