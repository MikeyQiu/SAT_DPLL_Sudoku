SAT Solver for Sudoku and General Problem<br>
=======
## Development environment<br>
Python 3.7<br>
## 1.Project's function<br>
This SAT solver can solve sudoku problem of 4x4,9x9 and 16x16 with specific format and general SAT problem with the input file format of DIMACS.<br>
The program will out put whether the input document is satisfiable, if so, it will give one of the possible solution.<br>
## 2.Getting started<br>
You can click the DPLL_heuristics.exe to run the problem.<br>
Or you can start by command line "python DPLL_heuristics.py "<br>
## 3.Project menu<br>
├── DPLL_heuristics     //.exe format for use<br>
├── DPLL_heuristics.py  //main body of the DPLL algorithm<br>
├── DPLL_origin.py      //original DPLL algorithm<br>
├── README.md<br>
├── heuristics.py       //heuristics of DPLL algorithm, included the PNR we proposed<br>
├── sudoku<br>
│   ├── cnf             //directory contained .cnf document, input for General SAT solver<br>
│   ├── csv             //directory contained .csv document, for SPSS analysis<br>
│   ├── out             //directory contained DIMACS document, output of DPLL<br>
│   └── txt             //directory contained Sudoku, input for Sudoku problem<br>
└── sudoku_rules        //directory contained DIMACS document, input of DPLL<br>
## 4.Q&A<br>
### 1. No such file or dictionary<br>
You need to input the name of document. For Sudoku problem, please input .txt document,like "9x9.txt"<br>
For general SAT problem, please input .cnf document,like "sample.cnf"<br>
### 2. Testing new document<br>
You can put your testing document in the corresponding directory named txt or cnf.<br>
### 3. Testing result<br>
The testing result could be find in out directory in the format of "name"+"number of heuristic"+.out. Once the process finished, a csv format can be also found in the directory.<br>
