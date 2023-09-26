#!/usr/bin/python3.8

import os
import sys
import operator

if __name__ == "__main__":

    f = open("strategies/scalping/backtesting/results.json", "r")
    results = {}
    for line in f:
        tokens = line.split('=')
        id = tokens[0]
        val = float(tokens[1])
        results[id] = val

    soreted_results = dict(
        sorted(results.items(), key=operator.itemgetter(1), reverse=True))

    negative_count = 0
    sum = 0.0
    for elem in soreted_results:
        value = soreted_results[elem]

        sum += value
        print(str(elem) + "   " + str(soreted_results[elem]))

        if value < 0:
            negative_count += 1

    print("Negative count = " + str(negative_count))
    print("Avg " + str(sum / 200.00))
    f.close()
