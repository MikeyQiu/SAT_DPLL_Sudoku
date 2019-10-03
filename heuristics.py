from DPLL_heuristics import decorator
from collections import defaultdict
import math
import random

def literalCounter(cnf, id):
    """
    Auxiliary function used to count occurrences of each literal in cnf
    Used for pure rule and heuristics
    :param cnf: list of clauses to count literals in
    :param id: id of chosen heuristic
    :return: dictionary k: literal, v: occurrences
    """

    # initialize dict
    counter = defaultdict(int)

    for clause in cnf:
        for literal in clause:
            if id == 'jw': # assign value according to jw heuristic
                counter[literal] += math.pow(2, -len(clause))
            else: # assign normal value
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

    elif id == 'pnr':
        combinedCounter = {}
        for key in counter:
            if -key in counter:
                if -key not in combinedCounter and key not in combinedCounter:
                    # get ratio of positive literals:negative literals
                    ratio = counter[abs(key)] / counter[-abs(key)]
                    if counter[key] > counter[-key]:
                        combinedCounter[key] = ratio
                    else:
                        combinedCounter[-key] = ratio
                else:
                    pass
            else:
                combinedCounter[key] = 1
        return combinedCounter
    return counter


@decorator
def randomStrategy(cnf):
    """
    Randomly choose a literal from clause list
    :param cnf: clause list
    :return: literal
    """
    counter = literalCounter(cnf, '')
    if counter:
        keys = list(counter)
        return random.choice(keys)


@decorator
def jeroslow_wangStrategy(cnf):
    counter = literalCounter(cnf, 'jw')
    count = {k: v for k, v in counter.items() if k >= 0}
    n = max(count, key=count.get)
    return n


@decorator
def DLCS(cnf):
    counter = literalCounter(cnf, 'dlcs')
    n = sorted(counter.items(), key=lambda x: x[1], reverse=True)
    for k,v in n:
        if k>0:
            return k
    n = max(counter, key=counter.get)
    return n

@decorator
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

@decorator
def PNR(cnf):
    counter = literalCounter(cnf, 'pnr')
    return max(counter, key=counter.get)