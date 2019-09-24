#!/usr/bin/python
# -*- coding: utf-8 -*-


import sys
import numba
from numba import jit, autojit
import os.path
import math
import random
from collections import defaultdict
import time
import pandas as pd

arr = [0]
arr2 = [0]
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
    row = 1
    col = 1
    if n < 4:
        for num in line:
            if num != "." and num != "\n":
                s = str(row) + str(col) + str(num)
                cnf.append(s)
            col += 1
            if col == n * n + 1:
                col = 1
                row += 1
    else:
        for num in line:
            if num != "." and num != "\n":
                if num.isalpha():
                    # print(num)
                    if num == 'G':
                        num = 16
                    else:
                        num = int('0x' + num, 16)
                        # print(num)
                s = str(17 * 17 * row + 17 * col + int(num))
                cnf.append(s)
            col += 1
            if col == n * n + 1:
                col = 1
                row += 1

    # write the initial numbers and sudoku rules into a single DIMACS file
    with open('sudoku/cnf/' + root + '.cnf', mode='w') as fq:
        fq.truncate()
        if n == 3:
            fp = open('sudoku_rules/sudoku-rules.txt', 'r')
        elif n == 2:
            fp = open('sudoku_rules/sudoku-rules-4x4.txt', 'r')
        elif n == 4:
            fp = open('sudoku_rules/sudoku-rules-16x16.txt', 'r')
        fq = open('sudoku/cnf/' + root + '.cnf', 'a')  # use "a" as append
        for line in fp:
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
    for line in open('sudoku/cnf/' + name + ".cnf", 'r'):
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


def tautologyRule(cnf, result):
    simplified = []
    c1 = literalCounter(cnf, '')
    for clause in cnf:
        counter = {}
        flag = True
        for literal in clause:
            if literal not in counter.keys():
                counter[literal] = 1  # first time appear
            else:
                counter[literal] += 1
        for k in counter:
            if -k in counter:
                flag = False
        if flag == True:
            simplified.append(clause)
    c2 = literalCounter(simplified, '')
    result = list(set(abs(i) for i in c1.keys()) - set(
        abs(j) for j in c2.keys()))  # If the variable have been eliminated during the process,give a value
    return simplified, result


'''
#description:An Auxiliary function used to count the number of appearence of each literal in the cnf,
used for pure rule and herurestic strategy
#input :list of clauses
#output :dictionary{(literal,times of appearence)}
'''


def literalCounter(cnf, id):
    counter = defaultdict(int)
    for clause in cnf:
        for literal in clause:
            if id == 'jw':
                counter[literal] += math.pow(2, -len(clause))
            else:
                counter[literal] += 1
    if id == 'dlcs':
        combinedCounter = {}
        for key in counter:
            if -key in counter:
                if counter[key] > counter[-key]:
                    combinedCounter[key] = counter[key] + counter[-key]
                else:
                    combinedCounter[-key] = counter[key] + counter[-key]
            else:
                combinedCounter[key] = counter[key]
        return combinedCounter
    else:
        return counter


'''
#description:An Auxiliary function used to eliminate clauses with given truth value 
# if the matching key has been found, remove the erntire clause
# if the oppostie value of matching key has been found, just remove the literal from the clause
#input :list of clauses, given Truth value
#output :list of clauses(after simplified)
'''


# @jit(nopython=True)
def simplify(cnf, literal):
    simplified = []
    for clause in cnf:
        if literal in clause:  # exact match, skip entire clause
            continue
        if -literal in clause:  # match but negative value, remove the negative value,remain the others
            tempClause = [i for i in clause if i != -literal]
            if len(tempClause) == 0:  # the -literal is a unit clause, which means the selection is wrong.
                return -1  # return for backtrack
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
    counter = literalCounter(cnf, '')
    result = []
    pureValues = []
    for k, v in counter.items():
        if -k not in counter.keys():  # only positive or only nagetive value in the counter
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
    t0 = time.process_time()
    timeout = time.time() + 5 * 60
    result = []
    unit_clauses = [i for i in cnf if len(i) == 1]
    while len(unit_clauses) > 0:
        if time.time() > timeout:
            return -1, []
        literal = unit_clauses[0][0]  # first literal of first clause
        cnf = simplify(cnf, literal)  # literal
        result += [literal]
        if cnf == -1:  # simplified returned error selection
            t1 = time.process_time()
            arr.append(round(t1 - t0, 6))
            return -1, []  # request for backtrack
        if not cnf:  # everything vanished
            t1 = time.process_time()
            arr.append(round(t1 - t0, 6))
            return cnf, result
        unit_clauses = [i for i in cnf if len(i) == 1]
    t1 = time.process_time()
    arr.append(round(t1 - t0, 6))
    return cnf, result


'''
#description:#The most trival split strategy: random choose form the given variables
#input :list of clauses
#output :random choice of variable 
'''
#add a decorator for couting function calls
def decorater(fun):
    def helper(x):
        helper.count+=1
        return fun(x)
        # print("被调用%d次。"%(count))
    helper.count=0
    return helper

@decorater
def randomStretegy(cnf):
    counter = literalCounter(cnf, '')
    keys = list(counter)
    if counter:
        return random.choice(keys)

@decorater
def jeroslow_wangStrategy(cnf):
    counter = literalCounter(cnf, 'jw')
    # n = sorted(counter.items(), key=lambda x: x[1], reverse=True)
    # print(n)
    n = max(counter, key=counter.get)
    print(n)
    # arr3.append(1)
    return n

@decorater
def DLCS(cnf):
    counter = literalCounter(cnf, 'dlcs')
    # n = sorted(counter.items(), key=lambda x: x[1], reverse=True)
    # print(n)
    n = max(counter, key=counter.get)
    print(n)
    return n


'''
#description: The function used to recurse, recursion depending on choose whether + or - value
#input :list of clauses,the result of variables
#output :a solution contains list of clauses and result.
'''


def DPLLbackTrack(cnf, result, backtrackTimes, splitTimes, heuristic_option):
    timeout = time.time() + 5 * 60  # 5 mins from now
    # cnf, pure_result = pureRule(cnf)
    cnf, unit_result = unitRule(cnf)
    result = result + unit_result
    # print(result)
    if cnf == -1 or time.time() > timeout:
        return []
    if not cnf:  # everything has been vanished
        array=["randomStretegy","jeroslow_wangStrategy","DLCS"]
        splitTimes=eval(array[heuristic_option]).count
        print(splitTimes)
        eval(array[heuristic_option]).count=0
        return result, backtrackTimes, splitTimes
    if heuristic_option == 0:
        luckyLiteral = randomStretegy(cnf)
    elif heuristic_option == 1:
        luckyLiteral = jeroslow_wangStrategy(cnf)
    elif heuristic_option == 2:
        luckyLiteral = DLCS(cnf)
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


def DPLL(name, heuristic_option, csv_result):
    t0 = time.process_time()
    cnf, max_var = dimacsParser(name)
    result = []
    # cnf, result = tautologyRule(cnf, [])
    # print(time.process_time())
    solution = DPLLbackTrack(cnf, result, 0, 0, heuristic_option)
    temp_csv_result = []
    deduction_time = 0
    for i in arr:
        deduction_time += i
    if solution:
        result, bt, sp = solution
        # sp=0
        # for i in arr3:
        #     sp += i
        result.sort(key=lambda x: abs(x))
        t1 = round(time.process_time() - t0, 4)
        print('s SAT')
        print('s d Time ' + str(deduction_time) + 's')
        print('s Solve Time ' + str(t1) + 's')
        print('s BackTrack Times ' + str(bt))
        print('s Split Times ' + str(sp))
        print('v ' + ' '.join([str(x) for x in result]) + ' 0')
        temp_csv_result.append("SAT")
        temp_csv_result.append(t1)
        temp_csv_result.append(deduction_time)
        temp_csv_result.append(bt)
        temp_csv_result.append(sp)
        csv_result.append(temp_csv_result)
        with open('sudoku/out/' + root + str(heuristic_option) + '.out', mode='a') as fq:
            fq.write('s SAT' + '\n')
            fq.write('s Solve Time ' + str(t1) + 's' + '\n')
            fq.write('s Deduction Time ' + str(deduction_time) + 's' + '\n')
            fq.write('s BackTrack Times ' + str(bt) + '\n')
            fq.write('s Split Times ' + str(sp) + '\n')
            fq.write('v ' + ' '.join([str(x) for x in result]) + ' 0' + '\n')
            fq.close()
    else:
        print('s not SAT')
        with open('sudoku/out/' + root + str(heuristic_option) + '.out', mode='a') as fq:
            fq.write('s not SAT\n')
        temp_csv_result.append("not SAT")
        temp_csv_result.append(0)
        temp_csv_result.append(0)
        temp_csv_result.append(0)
    arr.clear()


if __name__ == '__main__':
    quesitionType = int(input("Type of problem:\n1 sudoku \n2 General SAT\n"))
    numpre_name = input("route path of your puzzle : ")  # 9x9.txt
    heuristic_option = int(input("heuristic you would like to choose, input the digit:"
                                 "\n0 RANDOM "
                                 "\n1 Jeroslow_Wang"
                                 "\n2 DLCS"
                                 "\n"))
    root, ext = os.path.splitext(numpre_name)  # SPLIT the name with document suffix
    if quesitionType == 1:
        print("********************SAT Sudoku Solver********************")
        csv_result = []
        for line in open('sudoku/txt/' + numpre_name, 'r'):
            convert2cnf(line)
            DPLL(numpre_name, heuristic_option, csv_result)

        name = ['result', 'solving Time', 'deduction Time', 'backtracks', 'splits']
        test = pd.DataFrame(columns=name, data=csv_result)
        # print(test)
        test.to_csv('sudoku/csv/' + numpre_name + str(heuristic_option) + '.csv', encoding='gbk')
    if quesitionType == 2:
        print("********************General SAT Solver********************")
        with open('sudoku/cnf/' + numpre_name, 'r'):
            DPLL(numpre_name, heuristic_option, [])
