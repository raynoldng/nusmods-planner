# NUS Mods Planner

Python scripts that NUSMods Planner's server invokes to transform timetable query into first order logic. It also supports extracting the timetable after z3 solves the first order logic formula for completeness.

For details on the problem representation and algorithms to extract the timetable after solving, see the technical report [here](https://github.com/raynoldng/orbital-splashdown/blob/master/Splashdown_Technical_Report.pdf) 

It's main purpose is to translate timetable query into a first order logic formula in SMTLIB2 input format for use with any SMT solver. 

Features:

- free day planner
  - returns a timetable of provided modules that gives a free day
- timetable planning from subset of provided modules
- blocked hours, no lessons during indicated hours
- no lessons during lunch hours (12pm to 2pm)

## Getting Started

## Prerequisites
Requries [z3](https://github.com/Z3Prover/z3), install on your local machine with python bindings enabled

```
git clone https://github.com/Z3Prover/z3
cd z3
python scripts/mk_make.py --python
cd build
make sudo make install

```

Or you can install it using `pip`

```
pip install z3-solver

```
- Python 2.7
- requests

## Usage

See tests for sample use cases

## Others

This repository is part of NUSMods Planner, an augmented version of [NUSMods](https://nusmods.com) that comes with autmatic timetable generation subject to user specified constraints.

See it in action at [NUSMods Planner](https://modsplanner.tk)

## Authors

- [Bay Wei Heng](https://github.com/bayweiheng)
- Raynold Ng

## License
MIT License

## Acknowledgements

Special thanks to Li Kai and Zhi An for mentoring us.
