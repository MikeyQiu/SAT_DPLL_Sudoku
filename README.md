#SAT Solver for Sudoku and General SAT Problem
##Development environment
Python 3.7
##1.Project's goal
SAT solver for sudoku problem and general SAT problem with the input file format of DIMACS.

The program will out put whether the input document is satisfiable, if so, it will give one of the possible solution.
##2.Getting started
You can click the DPLL_heuristics.exe to run the problem.
Or you can start by command line "python DPLL_heuristics.py "
##3.Project menu
├── DPLL_heuristics     //.exe format for use
├── DPLL_heuristics.py  //main body of the DPLL algorithm
├── DPLL_heuristics.spec//pyinstaller specification
├── DPLL_origin.py      //original DPLL algorithm
├── README.md
├── frozen_dir.py       
├── heuristics.py       //heuristics of DPLL algorithm, included the PNR we proposed
├── sudoku
│   ├── cnf             //directory contained .cnf document, input for General SAT solver
│   ├── csv             //directory contained .csv document, for SPSS analysis
│   ├── out             //directory contained DIMACS document, output of DPLL
│   └── txt             //directory contained Sudoku, input for Sudoku problem
└── sudoku_rules        //directory contained DIMACS document, input of DPLL
##4.Q&A
1. No such file or dictionary
You need to input the name of document. For Sudoku problem, please input .txt document,like "9x9.txt"
For general SAT problem, please input .cnf document,like "sample.cnf"
2. Testing new document
You can put your testing document in the corresponding directory named txt or cnf.
3. Testing result
The testing result could be find in out directory in the format of "name"+"number of heuristic"+.out. Once the process finished, a csv format can be also found in the directory.
