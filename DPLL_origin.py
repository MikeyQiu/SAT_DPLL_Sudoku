#!/usr/bin/python
# -*- coding: utf-8 -*-


import sys
import os.path
import math
import random

cnf = []
'''
#description: script turn given sudoku document into cnf formula document
#input :sudoku txt document
#output :cnf formula document combied with sudoku rules(end with .cnf)
'''


def convert2cnf(name):
    arr = []
    for line in open(name, 'r'):
        l = len(line)
        n = math.sqrt((math.sqrt(l)))
    print("  square number sudoku plate problem : " + str(n) + "^2")
    # Reading the sudoku problem and chang it into the X-Y-Num Coding
    for line in open(name, 'r'):
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
        fp = open('sudoku-rules.txt', 'r')
        for line in fp:
            fq = open(root + '.cnf', 'a')  # use "a" as append
            fq.write(line)
        for s in cnf:
            fq.write(s + " 0" + '\n')
        fq.close()
        fp.close()
    return n


'''
#description: script read DIMACS document into python
#input :cnf document
#output :list contains clauses and the value of variable
#####reference on#####
#https://github.com/mxklabs/mxklabs-python/tree/master/mxklabs/dimacs
'''


def dimacsParser(name):
    cnf = list()
    cnf.append(list())
    maxvar = 0
    name = name.split(".")[0]
    # print(name)
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
    print(cnf)
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
    return (cnf)


'''
#description:An Auxiliary function used to count the number of appearence of each literal in the cnf,
used for pure rule and herurestic strategy
#input :list of clauses
#output :dictionary{(literal,times of appearence)}
'''


def literalCounter(cnf):
    counter = {}
    for clause in cnf:
        for literal in clause:
            if literal not in counter.keys():
                counter[literal] = 1  # first time appear
            else:
                counter[literal] += 1
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
    counter = literalCounter(cnf)
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

    while len(unit_clauses) > 0:
        unit = unit_clauses[0]
        cnf = simplify(cnf, unit[0])
        result += [unit[0]]
        if cnf == -1:
            return -1, []
        if not cnf:
            return cnf, result
        unit_clauses = [i for i in cnf if len(i) == 1]
    return cnf, result


'''
#description:#The most trival split strategy: random choose form the given variables
#input :list of clauses
#output :random choice of variable 
'''


def splitStrategy(cnf):
    counter = literalCounter(cnf)
    return random.choice(counter.keys())


'''
#description: The function used to recurse, recursion depending on choose whether + or - value
#input :list of clauses,the result of variables
#output :a solution contains list of clauses and result.
'''


def DPLLbackTrack(cnf, result):
    cnf, pure_result = pureRule(cnf)
    cnf, unit_result = unitRule(cnf)
    result = result + pure_result + unit_result
    if cnf == -1:
        return []
    if not cnf:  # everything has been vanished
        return result
    # split
    luckyLiteral = splitStrategy(cnf)
    solution = DPLLbackTrack(simplify(cnf, luckyLiteral), result + [luckyLiteral])
    if not solution:  # chose the opposite value to backtrack
        solution = DPLLbackTrack(simplify(cnf, -luckyLiteral), result + [-luckyLiteral])
    return solution


'''
#description: The main algorithm function
#input :txt document
#output :a solution document in the format of DIMACS
'''


def DPLL(name):
    cnf, max_var = dimacsParser(name)
    cnf = tautologyRule(cnf)
    solution = DPLLbackTrack(cnf, [])
    if solution:
        solution += [x for x in range(1, max_var + 1) if x not in solution and -x not in solution]
        solution.sort(key=lambda x: abs(x))
        print ('s SAT')
        print ('v ' + ' '.join([str(x) for x in solution]) + ' 0')
        with open(root + '.out', mode='w') as fq:
            fq.write('s SAT\n')
            fq.write('v ' + ' '.join([str(x) for x in solution]) + ' 0')
            fq.close()
    else:
        print ('s not SAT')
        with open(root + '.out', mode='w') as fq:
            fq.write('s not SAT\n')


if __name__ == '__main__':
    numpre_name = raw_input("route path of your puzzle : ")
    root, ext = os.path.splitext(numpre_name)
    print("********************SAT Sudoku Solver********************")
    convert2cnf(numpre_name)
    DPLL(numpre_name)
