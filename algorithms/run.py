#!/usr/bin/env python
""" Automatically generated documentation for run """

import argparse
import math

import core.distribution
import generation.entry
import visualization
from algorithms import marcoMatcher, lagEM, munkresMatcher
from core import sequence
from core.Timer import Timer
from core.distribution import NormalDistribution
from core.rule import Rule
from generation.generator import Generator


def printResult(result, distributions):
    print("Final parameters:")
    for key, value in result.items():
        print("\t {}: {}".format(key, value))
    if (distributions is not None):
        print("True parameters:")
        for d in distributions:
            print("\t {}".format(str(d)))

    # TODO remove again
    eventsA = seq.getEvents('A')
    eventsB = seq.getEvents('B')
    mean = 0
    for i in range(len(eventsB)):
        mean += eventsB[i].timestamp - eventsA[i].timestamp
    mean /= len(eventsB)

    var = 0
    for i in range(len(eventsB)):
        var += (eventsB[i].timestamp - eventsA[i].timestamp - mean) ** 2
    var = math.sqrt(var / len(eventsB))
    print("Empirical parameters:\n\tMu: {}\n\tSigma: {}".format(mean, var))


def printDistance(dist1, dist2):
    print("Distance:")
    print("\tKS Test: " + str(core.distribution.kstest(dist1, dist2)))
    # print("\tChi2 Test: " + str(core.distribution.chi2test(dist1, dist2)))


parser = argparse.ArgumentParser()
parser.add_argument("-r", "--rules", action="store", type=str, help="Path to files containing correct rules")
parser.add_argument("-i", "--input", action="store", type=str, help="Path to files containing sequences")
parser.add_argument("-a", "--algorithm", action="store", type=str, required=True, help="Algorithm to use for alignment")
parser.add_argument("-l", "--length", action="store", type=int, help="Length of to be generated sequence")
parser.add_argument("-c", "--count", action="store", type=int, help="Number of events in generated sequence")
parser.add_argument("-t", "--threshold", action="store", type=float, help="Threshold for convergence", default=0.01)

args = parser.parse_args()
print(args)

seq = None
baseRules = []
baseDistributions = []

if (args.input is None):
    if (args.rules is None):
        print("Neither rules nor input specified. Please provide at least one")
        exit(1)
    else:
        if (args.length is None and args.count is None):
            print("Neither sequence length nor event count specified. Please provide at exactly one")
            exit(1)
        if (args.length is not None and args.count is not None):
            print("Sequence length and event count specified. Please provide exactly one")
            exit(1)

        print("Creating new sequence from {} with length {}".format(args.rules, args.length))
        entries = generation.entry.loadEntries(args.rules)
        for entry in entries:
            baseRules.append(entry.rule)
            baseDistributions.append(entry.rule.distribution)

        gen = Generator().setEntries(entries)
        if (args.length is not None):
            seq = gen.setSeqLength(args.length).createSequence(1)[0]
        if (args.count is not None):
            seq = gen.setNumberOfEvents(args.count).createSequence(1)[0]
        seq.rules = baseRules
else:
    print("Loading sequence from {}".format(args.input))
    seq = sequence.loadFromFile(args.input)

print("Processing sequence:")
print(str(seq))

timer = Timer()
param = None
if (args.algorithm == marcoMatcher.MarcoMatcher.__name__):
    algorithm = marcoMatcher.MarcoMatcher()

    timer.start()
    param = algorithm.match(sequence=seq, eventA="A", eventB="B", algorithm="cvxopt")
    timer.stop()

elif (args.algorithm == munkresMatcher.MunkresMatcher.__name__):
    algorithm = munkresMatcher.MunkresMatcher()

    timer.start()
    param = algorithm.match(sequence=seq, eventA="A", eventB="B")
    timer.stop()

elif (args.algorithm == lagEM.lagEM.__name__):
    algorithm = lagEM.lagEM()

    timer.start()
    param = algorithm.match(sequence=seq, eventA="A", eventB="B", threshold=args.threshold)
    timer.stop()

if (param is None):
    print("Unknown algorithm: '{}'".format(args.algorithm))
    exit(1)
else:
    resultDist = NormalDistribution(param["Mu"], param["Sigma"])
    rule = Rule("A", "B", resultDist)
    seq.calculatedRules = [rule]

    printResult(param, baseDistributions)
    print("Calculation time: {} minutes".format(timer))
    printDistance(resultDist, baseDistributions[0])
    visualization.getAreaBetweenDistributions(resultDist, baseDistributions[0])
    visualization.showDistributions(resultDist, baseDistributions[0])
    visualization.showVisualizer(seq)
