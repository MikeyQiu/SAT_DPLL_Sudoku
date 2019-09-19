#!/usr/bin/python
# -*- coding: utf-8 -*-


import sys
import os.path
import math
import random
import collections
import time

# cnf = []
'''
#description: script turn given sudoku document into cnf formula document
#input :sudoku txt document
#output :cnf formula document combied with sudoku rules(end with .cnf)
'''


def convert2cnf(line):
    cnf = []
    l = len(line)
    n = int(math.sqrt((math.sqrt(l))))
    print("  square number sudoku plate problem : " + str(n) + "^2")
    # Reading the sudoku problem and chang it into the X-Y-Num Coding

    # for line in open(name, 'r'):
    # str_row = (line[:-1].split(','))
    row = 1
    col = 1
    for num in line:
        if num != ".":
            s = str(row) + str(col) + str(num)
            cnf.append(s)
        col += 1
        if col == n * n + 1:
            col = 1
            row += 1

    # write the initial numbers and sudoku rules into a single DIMACS file
    with open(root + '.cnf', mode='w') as fq:
        fq.truncate()
        fp = open('sudoku-rules.txt', 'r')
        for line in fp:
            fq = open(root + '.cnf', 'a')  # use "a" as append
            fq.write(line)
        for s in cnf:
            fq.write(s + " 0" + '\n')
        fq.close()
        fp.close()
    # return n


'''
#description: script read DIMACS document into python
#input :cnf document
#output :list contains clauses and the value of variable
#***************************reference on*********************************#
#https://github.com/mxklabs/mxklabs-python/tree/master/mxklabs/dimacs
'''


def dimacsParser(name):
    cnf = list()
    cnf.append(list())
    maxvar = 0
    name = name.split(".")[0]
    for line in open(name + ".cnf", 'r'):
        tokens = line.split()
        if len(tokens) != 0 and tokens[0] not in ("p", "c"):
            for tok in tokens:
                lit = int(tok)
                maxvar = max(maxvar, abs(lit))
                if lit == 0:
                    cnf.append(list())
                else:
                    cnf[-1].append(lit)

    assert len(cnf[-1]) == 0
    cnf.pop()
    # print(cnf)
    return (cnf, maxvar)


'''
#description:A function used to check tautology at the beginning of the DPLL
#input :list of clauses
#output :list of clauses(without tautology clauses)
'''


def tautologyRule(cnf):
    # tautology check
    for clause in cnf:
        if len(clause) > 1:
            clause.sort()
            i, j, = 0, len(clause) - 1
            while (i <= j):
                if clause[i] == -clause[j]:
                    del clause[:]  # delete the clause out of the cnf
                    break
                elif clause[i] < -clause[j]:
                    i += 1
                else:
                    j -= 1
    return cnf


'''
#description:An Auxiliary function used to count the number of appearence of each literal in the cnf,
used for pure rule and herurestic strategy
#input :list of clauses
#output :dictionary{(literal,times of appearence)}
'''


def literal_in_clause_Counter(cnf):
    counter = {}
    for clause in cnf:
        literal_in_clause = {}
        for literal in clause:
            if literal not in counter.keys():
                counter[literal] = 1  # first time appear
            if literal in counter.keys():
                if literal not in literal_in_clause.keys():
                    counter[literal] += 1
                    literal_in_clause[literal] = 1
    return counter


'''
#description:An Auxiliary function used to eliminate clauses with given truth value 
# if the matching key has been found, remove the erntire clause
# if the oppostie value of matching key has been found, just remove the literal from the clause
#input :list of clauses, given Truth value
#output :list of clauses(after simplified)
'''


def simplify(cnf, literal):
    simplified = []
    for clause in cnf:
        if literal in clause:  # exact match, skip entire clause
            continue
        if -literal in clause:  # match but negative value, remove the negative value,remain the others
            tempClause = []
            for l in clause:
                if l != -literal:
                    tempClause.append(l)
            if len(tempClause) == 0:
                return -1  # the set has been empty
            simplified.append(tempClause)
        else:
            simplified.append(clause)
    return simplified


'''
#description:Afunction used to judge whether the literal in clauses is pure
#input :list of clauses
#output :list of clauses(after simplified),result of truth value
'''


def pureRule(cnf):
    counter = literal_in_clause_Counter(cnf)
    result = []
    pureValues = []
    for k, v in counter.items():
        if -k not in counter:  # only positive or only nagetive value in the counter
            pureValues.append(k)
    for pure in pureValues:
        cnf = simplify(cnf, pure)
    result += pureValues
    return cnf, result


'''
#description:function used to judge whether the literal in clauses is a unit clause
#input :list of clauses
#output :list of clauses(after simplified),result of truth value
'''


def unitRule(cnf):
    unit_clauses = []
    result = []
    for literal in cnf:
        if len(literal) == 1:
            unit_clauses.append(literal)

    while unit_clauses:
        unit = unit_clauses[0]  # list
        cnf = simplify(cnf, unit[0])  # literal
        result += [unit[0]]
        if cnf == -1:  # simplified returned empty
            return -1, []  # backtrack
        if not cnf:  # everything vanished
            return cnf, result
        unit_clauses = [i for i in cnf if len(i) == 1]
    return cnf, result


'''
#description:#The most trival split strategy: random choose form the given variables
#input :list of clauses
#output :random choice of variable 
'''


def splitStrategy(cnf):
    counter = literal_in_clause_Counter(cnf)
    return random.choice(counter.keys())


def jeroslow_wangStrategy(cnf):
    counter = literal_in_clause_Counter(cnf)
    n = sorted(counter.items(), key=lambda x: x[1], reverse=True)
    print (n)
    n = max(counter, key=counter.get)
    print (n)
    return n


'''
#description: The function used to recurse, recursion depending on choose whether + or - value
#input :list of clauses,the result of variables
#output :a solution contains list of clauses and result.
'''


def DPLLbackTrack(cnf, result, backtrackTimes, splitTimes, heuristic_option):
    # cnf, pure_result = pureRule(cnf)
    cnf, unit_result = unitRule(cnf)
    result = result + unit_result
    if cnf == -1:
        return []
    if not cnf:  # everything has been vanished
        return result, backtrackTimes, splitTimes
    # split
    # luckyLiteral = splitStrategy(cnf)  # base strategy
    if heuristic_option == 0:
        luckyLiteral = splitStrategy(cnf)
    elif heuristic_option == 1:
        luckyLiteral = jeroslow_wangStrategy(cnf)
    #######add your heruistic here############
    splitTimes += 1
    solution = DPLLbackTrack(simplify(cnf, luckyLiteral), result + [luckyLiteral], backtrackTimes, splitTimes,
                             heuristic_option)
    if not solution:  # chose the opposite value to backtrack
        solution = DPLLbackTrack(simplify(cnf, -luckyLiteral), result + [-luckyLiteral], backtrackTimes + 1, splitTimes,
                                 heuristic_option)
    return solution


'''
#description: The main algorithm function
#input :txt document
#output :a solution document in the format of DIMACS
'''


def DPLL(name, heuristic_option):
    t0 = time.clock()
    cnf, max_var = dimacsParser(name)
    cnf = tautologyRule(cnf)
    solution = DPLLbackTrack(cnf, [], 0, 0, heuristic_option)
    if solution:
        result, bt, sp = solution
        print(bt, sp)
        result.sort(key=lambda x: abs(x))
        t1 = time.clock() - t0
        print ('s SAT')
        print ('s Solve Time ' + str(t1) + 's')
        print ('s BackTrack Times ' + str(bt))
        print ('s Split Times ' + str(sp))
        print ('v ' + ' '.join([str(x) for x in result]) + ' 0')
        with open(root + '.out', mode='a') as fq:
            fq.write('s SAT' + '\n')
            fq.write('s Solve Time ' + str(t1) + 's' + '\n')
            fq.write('s BackTrack Times ' + str(bt) + '\n')
            fq.write('s Split Times ' + str(sp) + '\n')
            fq.write('v ' + ' '.join([str(x) for x in result]) + ' 0'+'\n')
            fq.close()
    else:
        print ('s not SAT')
        with open(root + '.out', mode='a') as fq:
            fq.write('s not SAT\n')


if __name__ == '__main__':
    quesitionType = int(raw_input("Type of problem:\n1 sudoku \n2 General SAT\n"))
    numpre_name = raw_input("route path of your puzzle : ")  # 1000 sudokus.txt
    heuristic_option = int(raw_input("heuristic you would like to choose, input the digit:"
                                 "\n0 RANDOM "
                                 "\n1 Jeroslow_Wang"
                                 "\n"))
    root, ext = os.path.splitext(numpre_name)  # SPLIT the name with document suffix
    if quesitionType == 1:
        print("********************SAT Sudoku Solver********************")
        for line in open(numpre_name, 'r'):
            convert2cnf(line)
            DPLL(numpre_name, heuristic_option)
    if quesitionType == 2:
        print("********************General SAT Solver********************")
        for line in open(numpre_name, 'r'):
            DPLL(numpre_name, heuristic_option)
