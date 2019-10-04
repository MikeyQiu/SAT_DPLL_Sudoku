#!/usr/bin/python
# -*- coding: utf-8 -*-
import frozen_dir
from heuristics import *
import os.path
import math
import time
import pandas as pd
import numpy as np

arr = [0]
array = ["randomStrategy", "jeroslow_wangStrategy", "DLCS","MOM", "PNR"]

############Change for the timeout ,the default is 60##################
TIMEOUT = 120


SETUP_DIR = frozen_dir.app_path()
print(SETUP_DIR)
def convert2cnf(line):
    """
    Turns given sudoku document into cnf formula document
    :param line: sudoku txt document
    :return: nothing, but writes to cnf document combined with sudoku rules
    """

    # initialize list
    cnf = []

    # get size
    l = len(line)
    size = int(math.sqrt((math.sqrt(l))))
    print("Sudoku size: " + str(size) + "^2")

    # Reading the sudoku problem and chang it into the X-Y-Num Coding
    row = 1
    col = 1
    if size < 4: # sudoku with only numbers
        for num in line:
            if num != "." and num != "\n":
                s = str(row) + str(col) + str(num)
                cnf.append(s)
            col += 1
            if col == size * size + 1:
                col = 1
                row += 1
    else: # take letters in account too
        for num in line:
            if num != "." and num != "\n":
                if num.isalpha():
                    if num == 'G':
                        num = 16
                    else:
                        num = int('0x' + num, 16)
                s = str(17 * 17 * row + 17 * col + int(num))
                cnf.append(s)
            col += 1
            if col == size * size + 1:
                col = 1
                row += 1

    # write the initial numbers and sudoku rules into a single DIMACS file
    with open(SETUP_DIR+'/sudoku/cnf/' + root + '.cnf', mode='w') as fq:
        fq.truncate()
        if size == 3:
            fp = open(SETUP_DIR+'/sudoku_rules/sudoku-rules.txt', 'r')
        elif size == 2:
            fp = open(SETUP_DIR+'/sudoku_rules/sudoku-rules-4x4.txt', 'r')
        elif size == 4:
            fp = open(SETUP_DIR+'/sudoku_rules/sudoku-rules-16x16.txt', 'r')
        fq = open(SETUP_DIR+'/sudoku/cnf/' + root + '.cnf', 'a')
        for clause in fp:
            fq.write(clause)
        for s in cnf:
            fq.write(s + " 0" + '\n')
        fq.close()
        fp.close()


def dimacsParser(name):
    """
    Reads DIMACS document into python
    Reference on https://github.com/mxklabs/mxklabs-python/tree/master/mxklabs/dimacs
    :param name: cnf document with all clauses
    :return: list containing the clauses
    """

    # initialize variables
    cnf = list()
    cnf.append(list())
    name = name.split(".")[0]

    # add clauses to list
    for line in open(SETUP_DIR+'/sudoku/cnf/' + name + ".cnf", 'r'):
        tokens = line.split()
        if len(tokens) != 0 and tokens[0] not in ("p", "c"):
            for tok in tokens:
                lit = int(tok)
                if lit == 0:
                    cnf.append([])
                else:
                    cnf[-1].append(lit)

    assert len(cnf[-1]) == 0
    cnf.pop()
    cnf = np.array(cnf)

    return cnf


def tautologyRule(cnf):
    """
    Used to check tautology at the beginning of the algorithm
    :param cnf: list of clauses
    :return: list of clauses without tautology clauses
    """

    # initialize variables
    simplified = []
    c1=literalCounter(cnf,"")

    # check for tautologies
    for clause in cnf:
        counter = {}
        flag = True
        for literal in clause:
            if literal not in counter.keys():
                counter[literal] = 1  # first time appear
            else:
                counter[literal] += 1
        # print(counter)
        for k in counter:
            if -k in counter:
                flag = False
        if flag is True:
            simplified.append(clause)
    # If the variable have been eliminated during the process,give it a value
    c2 = literalCounter(simplified, '')
    # print(c1)
    # print(c2)
    result = list(set(abs(i) for i in c1.keys()) - set(
        abs(j) for j in c2.keys()))
    return simplified, result



def simplify(cnf, literal):
    """
    Function used to eliminate clauses with given truth value
    :param cnf: list of clauses
    :param literal: given truth value
    :return: simplified list of clauses
    """
    # initialize list
    simplified = []

    for clause in cnf:
        if literal in clause:  # exact match, skip entire clause
            continue
        if -literal in clause:  # match but negative value, remove the negative value,remain the others
            tempClause = [i for i in clause if i != -literal]
            if len(tempClause) == 0:  # the -literal is an unit clause, which means the selection is wrong.
                return -1  # return for backtrack
            simplified.append(tempClause)
        else:
            simplified.append(clause)

    return simplified


def unitRule(cnf):
    """
    Function used to judge whether literal in clause is a unit clause
    :param cnf: list of clauses
    :return: simplified list of clauses, result list of truth values
    """

    # start timer
    t0 = time.process_time()
    result = []
    # get list of clauses with one literal
    unit_clauses = [i for i in cnf if len(i) == 1]

    # simplify all unit clauses
    while len(unit_clauses) > 0:

        literal = unit_clauses[0][0]  # first literal of first clause
        cnf = simplify(cnf, literal)  # literal
        result += [literal]

        if cnf == -1:  # simplify function returned error selection
            t1 = time.process_time()
            arr.append(round(t1 - t0, 6))
            return -1, []  # request for backtrack

        if not cnf:  # all clauses are satisfied
            t1 = time.process_time()
            arr.append(round(t1 - t0, 6))
            return cnf, result

        # update the list of unit clauses
        unit_clauses = [i for i in cnf if len(i) == 1]
    t1 = time.process_time()
    arr.append(round(t1 - t0, 6))

    return cnf, result


# a decorator for counting function calls
def decorator(fun):
    """
    Decorator for counting function calls
    :param fun: heuristic that gets called
    :return:
    """
    def helper(*args, **kwargs):
        helper.count += 1
        return fun(*args, **kwargs)
        # print("called %d times。"%(count))

    helper.count = 0
    return helper


backtrackTimes = 0
@decorator
def DPLLbackTrack(cnf, result, heuristic_option):
    """
    Function used for recursion
    :param cnf: list of clauses
    :param result: list with result so far
    :param heuristic_option: chosen heuristic
    :return:
    """
    # get backtrack times
    global backtrackTimes

    # check for unit clauses and add found clauses to result list
    cnf, unit_result = unitRule(cnf)
    result = result + unit_result

    # if the select value is wrong, return empty list to reselect a polarity
    if cnf == -1:
        return []

    if not cnf:  # everything has been vanished, success
        splitTimes = eval(array[heuristic_option]).count
        eval(array[heuristic_option]).count = 0  # reset the count to 0 for next move

        bt = backtrackTimes
        backtrackTimes = 0
        return result, bt, splitTimes

    # pick next literal to assign truth value to according to heuristic option
    luckyLiteral = eval(array[heuristic_option])(cnf)

    # recurse
    solution = DPLLbackTrack(simplify(cnf, luckyLiteral), result + [luckyLiteral],
                             heuristic_option)

    if not solution:  # choose the opposite value to backtrack
        backtrackTimes += 1
        solution = DPLLbackTrack(simplify(cnf, -luckyLiteral), result + [-luckyLiteral],
                                 heuristic_option)
    return solution


def output(flag, root, heuristic_option, solve_time, deduction_time, backtrack_time, split_time, result,
           csv_result):
    """
    Function to print output
    :param: params get passed on automatically
    :return: writes output to file
    """

    temp_csv_result = []

    if flag == "TIMEOUT":
        print('TIMEOUT')
        temp_csv_result.append("TIMEOUT")
    elif flag:
        print('s SAT')
        temp_csv_result.append("SAT")
    else:
        print('s NOT SAT')
        temp_csv_result.append("NOT SAT")

    # print output
    print('s Solve Time ' + str(solve_time) + 's')
    print('s Deduction Time ' + str(deduction_time) + 's')
    print('s BackTrack Times ' + str(backtrack_time))
    print('s Split Times ' + str(split_time))
    print('v ' + ' '.join([str(x) for x in result]) + ' 0')

    # append to csv output list
    temp_csv_result.append(solve_time)
    temp_csv_result.append(deduction_time)
    temp_csv_result.append(backtrack_time)
    temp_csv_result.append(split_time)
    csv_result.append(temp_csv_result)

    # write data to output file
    with open(SETUP_DIR+'/sudoku/out/' + str(root) + '_' + str(heuristic_option) + '.out', mode='a') as fq:
        if flag == "TIMEOUT":
            fq.write('s TIMEOUT' + '\n')
        elif flag:
            fq.write('s SAT' + '\n')
        else:
            fq.write('s NOT SAT' + '\n')
        fq.write('s Solve Time ' + str(solve_time) + 's' + '\n')
        fq.write('s Deduction Time ' + str(deduction_time) + 's' + '\n')
        fq.write('s BackTrack Times ' + str(backtrack_time) + '\n')
        fq.write('s Split Times ' + str(split_time) + '\n')
        fq.write('v ' + ' '.join([str(x) for x in result]) + ' 0' + '\n')
        fq.close()


def DPLL(name, heuristic_option, csv_result):
    """
    Main DPLL function in which the recursive function gets called
    parameters get passed on automatically
    :return: passes parameters on to output function
    """

    t0 = time.process_time()
    cnf = dimacsParser(name)

    cnf, result= tautologyRule(cnf)
    result, backtrack_time, split_time = DPLLbackTrack(cnf, result, heuristic_option)

    deduction_time = 0
    for i in arr:
        deduction_time += i
    deduction_time = round(deduction_time, 4)
    # give postive values to those variable being vanishede that doesn't influence the result
    c1 = literalCounter(cnf, '')
    c2= set([abs(i) for i in result])
    result += list(set(abs(i) for i in c1.keys())-c2)
    result.sort(key=lambda x: abs(x))
    t1 = round(time.process_time() - t0, 4)
    flag = result

    output(flag, root, heuristic_option, t1, deduction_time, backtrack_time, split_time, result, csv_result)
    arr.clear()


if __name__ == '__main__':

    # validate input
    questionTypes = ['1', '2']
    questionType = input("Type of problem:\n1 sudoku \n2 General SAT\n")
    while questionType not in questionTypes:
        questionType = input("Please enter 1 for sudoku and 2 for general SAT.\n1 sudoku \n2 General SAT\n")
    questionType = int(questionType)

    numpre_name = input("document name of your puzzle : \n.txt for sudoku and .cnf for general SAT\n")

    heuristics = ['0', '1', '2', '3', '4']
    heuristic_option = input("""Please enter the number of the heuristic you would like to choose:
                                 0 RANDOM 
                                 1 Jeroslow_Wang
                                 2 DLCS
                                 3 MOM
                                 4 PNR\n""")
    while heuristic_option not in heuristics:
        heuristic_option = input("""Please choose one of following numbers:
                                 0 RANDOM 
                                 1 Jeroslow_Wang
                                 2 DLCS
                                 3 MOM
                                 4 PNR\n""")
    heuristic_option = int(heuristic_option)

    root, ext = os.path.splitext(numpre_name)  # SPLIT the name with document suffix

    if questionType == 1:

        print("********************SAT Sudoku Solver********************")

        csv_result = []
        name = ['result', 'solving Time', 'deduction Time', 'backtracks', 'splits']

        for line in open(SETUP_DIR+'/sudoku/txt/' + numpre_name, 'r'):

            convert2cnf(line)
            DPLL(numpre_name, heuristic_option, csv_result)

            test = pd.DataFrame(columns=name, data=csv_result)
            test.to_csv(SETUP_DIR+'/sudoku/csv/' + numpre_name +'_'+str(heuristic_option) + '.csv', encoding='gbk')

    if questionType == 2:
        print("********************General SAT Solver********************")
        with open(SETUP_DIR+'/sudoku/cnf/' + numpre_name, 'r'):
            DPLL(numpre_name, heuristic_option, [])
