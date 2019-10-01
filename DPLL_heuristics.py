#!/usr/bin/python
# -*- coding: utf-8 -*-


import os.path
import math
import random
from collections import defaultdict
import time
import pandas as pd
import numpy as np
import signal

arr = [0]
array = ["randomStretegy", "jeroslow_wangStrategy", "DLCS","MOM"]
############Change for the timeout ,the defalut is 60##################
TIMEOUT = 120
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
                    cnf.append([])
                else:
                    cnf[-1].append(lit)

    assert len(cnf[-1]) == 0
    cnf.pop()
    cnf=np.array(cnf)
    # print(cnf)
    # print(cnf.shape)
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
        abs(j) for j in c2.keys()))  # If the variable have been eliminated during the process,give it a value
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
    cnf=simplified
    return cnf


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
    # print("URSTART")
    # print(cnf)
    t0 = time.process_time()
    result = []
    unit_clauses = [i for i in cnf if len(i) == 1]
    while len(unit_clauses) > 0:
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
    # print("UREND")
    # print(cnf)
    return cnf, result


'''
#description:#The most trival split strategy: random choose form the given variables
#input :list of clauses
#output :random choice of variable 
'''


# a decorator for couting function calls
def decorater(fun):
    def helper(*args, **kwargs):
        helper.count += 1
        return fun(*args, **kwargs)
        # print("called %d times。"%(count))

    helper.count = 0
    return helper


# a decorator for counting timeout
def set_timeout(num, callback):
    def wrap(func):
        def handle(signum, frame):  # 收到信号 SIGALRM 后的回调函数，第一个参数是信号的数字，第二个参数是the interrupted stack frame.
            raise RuntimeError

        def to_do(*args, **kwargs):
            try:
                signal.signal(signal.SIGALRM, handle)  # 设置信号和回调函数
                signal.alarm(num)  # 设置 num 秒的闹钟
                # print('start alarm signal.')
                r = func(*args, **kwargs)
                # print('close alarm signal.')
                signal.alarm(0)  # 关闭闹钟
                return r
            except RuntimeError as e:
                callback(csv_result)

        return to_do

    return wrap


@decorater
def randomStretegy(cnf):
    counter = literalCounter(cnf, '')
    # counter = sorted(counter.items(), key=lambda x: x[1], reverse=True)
    # print(counter)
    keys = list(counter)
    #print(keys)
    if counter:
        k=random.choice(keys)
        # k=max(counter, key=counter.get)
        print(k)
        return k


@decorater
def jeroslow_wangStrategy(cnf):
    counter = literalCounter(cnf, 'jw')
    n = max(counter, key=counter.get)
    return n


@decorater
def DLCS(cnf):
    counter = literalCounter(cnf, 'dlcs')
    n = sorted(counter.items(), key=lambda x: x[1], reverse=True)
    print(n)
    for k,v in n:
        if k>0:
            print(k,v)
            return k
    n = max(counter, key=counter.get)
    print(n)
    return n

@decorater
def MOM(cnf):
    def minClauses(cnf):
        minClauses = []
        size = -1
        for clause in cnf:
            clauseSize = len(clause)
            # Either the current clause is smaller
            if size == -1 or clauseSize < size:
                minClauses = [clause]
                size = clauseSize
            elif clauseSize == size:
                minClauses.append(clause)
        return minClauses
    minc = minClauses(cnf)
    counter = literalCounter(minc, '')
    # n = sorted(counter.items(), key=lambda x: x[1], reverse=True)
    # print(n)
    n = max(counter, key=counter.get)
    # print(n)
    return n

'''
#description: The function used to recurse, recursion depending on choose whether + or - value
#input :list of clauses,the result of variables
#output :a solution contains list of clauses and result.
'''
backtrackTimes=0
@decorater
def DPLLbackTrack(cnf, result, heuristic_option):
    global backtrackTimes
    # timeout= time.time() + 2 * 1  # 5 mins from now
    # print(timeout)
    cnf, unit_result = unitRule(cnf)
    # cnf, pure_result = pureRule(cnf)
    #print(pure_result)
    result = result + unit_result#+pure_result
    if cnf == -1:
        return []
    if not cnf:  # everything has been vanished
        splitTimes = eval(array[heuristic_option]).count
        eval(array[heuristic_option]).count = 0  # reset the count to 0 for next move
        # backtrackTimes=DPLLbackTrack.count
        # print(DPLLbackTrack.count)
        n=0
        bt=backtrackTimes
        backtrackTimes=0
        return result, bt, splitTimes
    luckyLiteral = eval(array[heuristic_option])(cnf)
    solution = DPLLbackTrack(simplify(cnf, luckyLiteral), result + [luckyLiteral],
                             heuristic_option)
    if not solution:  # chose the oppo
        # site value to backtrack
        # print("Before BackTracking")
        # print(backtrackTimes,result)
        backtrackTimes+=1
        solution = DPLLbackTrack(simplify(cnf, -luckyLiteral), result + [-luckyLiteral],
                                 heuristic_option)
    return solution


'''
#description: The main algorithm function
#input :txt document
#output :a solution document in the format of DIMACS
'''


def after_timeout(csv_result):  # call function after timeout
    arr.clear()
    splitTimes = eval(array[heuristic_option]).count
    # print(splitTimes)
    eval(array[heuristic_option]).count = 0  # reset the count to 0 for next move
    output("TIMEOUT", root, heuristic_option, TIMEOUT, 0, 0, splitTimes, [], csv_result)


def output(flag, root, heuristic_option, solve_time, deduction_time, backtrack_time, split_time, result,
           csv_result):
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
    print('s Solve Time ' + str(solve_time) + 's')
    print('s Deduction Time ' + str(deduction_time) + 's')
    print('s BackTrack Times ' + str(backtrack_time))
    print('s Split Times ' + str(split_time))
    print('v ' + ' '.join([str(x) for x in result]) + ' 0')

    temp_csv_result.append(solve_time)
    temp_csv_result.append(deduction_time)
    temp_csv_result.append(backtrack_time)
    temp_csv_result.append(split_time)
    csv_result.append(temp_csv_result)
    with open('sudoku/out/' + str(root) + '_' + str(heuristic_option) + '.out', mode='a') as fq:
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


# set the timelimit for the first variable
@set_timeout(TIMEOUT, after_timeout)  # 60s
def DPLL(name, heuristic_option, csv_result):
    t0 = time.process_time()
    cnf, max_var = dimacsParser(name)
    n=literalCounter(cnf,'')
    n = sorted(n.items(), key=lambda x: x[1], reverse=True)
    print(n)
    print(len(n))
    result = []
    # cnf, result = tautologyRule(cnf, [])
    # print(time.process_time())
    solution = DPLLbackTrack(cnf, result, heuristic_option)
    result, backtrack_time, split_time = solution
    deduction_time = 0
    for i in arr:
        deduction_time += i
    deduction_time = round(deduction_time, 4)
    result.sort(key=lambda x: abs(x))
    t1 = round(time.process_time() - t0, 4)
    flag = result
    # print(flag)
    output(flag, root, heuristic_option, t1, deduction_time, backtrack_time, split_time, result, csv_result)
    arr.clear()


if __name__ == '__main__':
    quesitionType = int(input("Type of problem:\n1 sudoku \n2 General SAT\n"))
    numpre_name = input("route path of your puzzle : ")  # 9x9.txt
    heuristic_option = int(input("heuristic you would like to choose, input the digit:"
                                 "\n0 RANDOM "
                                 "\n1 Jeroslow_Wang"
                                 "\n2 DLCS"
                                 "\n3 MOM"
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
        test.to_csv('sudoku/csv/' + numpre_name +'_'+str(heuristic_option) + '.csv', encoding='gbk')
    if quesitionType == 2:
        print("********************General SAT Solver********************")
        with open('sudoku/cnf/' + numpre_name, 'r'):
            DPLL(numpre_name, heuristic_option, [])
