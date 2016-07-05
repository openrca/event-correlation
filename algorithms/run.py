#!/usr/bin/env python
""" Automatically generated documentation for run """

import argparse
import math
import os

import core.distribution
import core.rule
import generation
import visualization
from algorithms import marcoMatcher, lagEM, munkresMatcher, RESULT_MU, RESULT_SIGMA, icpMatcher, RESULT_KDE, RESULT_IDX
from core import sequence, distribution
from core.Timer import Timer
from core.distribution import NormalDistribution
from core.performance import RangePerformance, VariancePerformance, StdPerformance, CondProbPerformance, \
    EntropyPerformance
from core.rule import Rule


def printResult(result, distribution, empiricalDist=None):
    print("Final parameters:")
    for key, value in result.items():
        if (key == RESULT_IDX and value is not None):
            print("\t {}: \n{}".format(key, value.T))
        else:
            print("\t {}: {}".format(key, value))
    if (distribution is not None):
        print("True parameters:\n\t{}".format(str(distribution)))
    if (empiricalDist is not None):
        print("Empirical parameters:\n\tMu: {}\n\tSigma: {}".format(empiricalDist.mu, empiricalDist.sigma))


def printDistance(dist1, dist2):
    if (dist1 is None or dist2 is None):
        return

    print("Distance:")
    print("\tKS Test: " + str(core.distribution.kstest(dist1, dist2)))
    # print("\tChi2 Test: " + str(core.distribution.chi2test(dist1, dist2)))


def printPerformance(dist, samples):
    if (dist is None):
        return

    print("Performance:")
    print("\tRange: {}".format(RangePerformance().getValueByDistribution(dist)))
    print("\tVariance: {}".format(VariancePerformance().getValueByDistribution(dist)))
    print("\tStd: {}".format(StdPerformance().getValueByDistribution(dist)))
    print("\tCondProd: {}".format(CondProbPerformance(samples=samples).getValueByDistribution(dist)))
    print("\tEntropy: {}".format(EntropyPerformance().getValueByDistribution(dist)))


parser = argparse.ArgumentParser()
parser.add_argument("-r", "--rules", action="store", type=str, help="Path to files containing correct rules")
parser.add_argument("-i", "--input", action="store", type=str, help="Path to file containing sequence")
parser.add_argument("-a", "--algorithm", action="store", type=str, required=True, help="Algorithm to use for alignment")
parser.add_argument("-l", "--length", action="store", type=int, help="Length of to be generated sequence")
parser.add_argument("-c", "--count", action="store", type=int, help="Number of events in generated sequence")
parser.add_argument("-t", "--threshold", action="store", type=float, help="Threshold for convergence", default=0.01)

args = parser.parse_args()
print(args)

seq = None
baseDistribution = None

if (args.input is None):
    if (args.rules.startswith("..")):
        args.rules = os.path.join(os.path.dirname(__file__), args.rules)

    seq = generation.createSequences(rules=args.rules, length=args.length, count=args.count)

    rules = core.rule.loadFromFile(args.rules)
    if (len(rules) == 1):
        baseDistribution = rules[0].distributionResponse

else:
    print("Loading sequence from {}".format(args.input))
    seq = sequence.loadFromFile(args.input)

print("Processing sequence:")
print(str(seq))

timer = Timer()
timer.start()
param = None
if (args.algorithm == marcoMatcher.MarcoMatcher.__name__):
    algorithm = marcoMatcher.MarcoMatcher()
    param = algorithm.match(sequence=seq, eventA="A", eventB="B", algorithm=marcoMatcher.Method.PULP)

elif (args.algorithm == munkresMatcher.MunkresMatcher.__name__):
    algorithm = munkresMatcher.MunkresMatcher()
    param = algorithm.match(sequence=seq, eventA="A", eventB="B")

elif (args.algorithm == lagEM.lagEM.__name__):
    algorithm = lagEM.lagEM()
    param = algorithm.match(sequence=seq, eventA="A", eventB="B", threshold=args.threshold)

elif (args.algorithm == icpMatcher.IcpMatcher.__name__):
    algorithm = icpMatcher.IcpMatcher()
    param = algorithm.match(sequence=seq, eventA="A", eventB="B", showVisualization=False, f="confidence")

timer.stop()

if (param is None):
    print("Unknown algorithm: '{}'".format(args.algorithm))
    exit(1)
else:
    empiricalDist = core.distribution.getEmpiricalDist(seq, "A", "B")
    resultDist = NormalDistribution(param[RESULT_MU], param[RESULT_SIGMA])
    rule = Rule("A", "B", resultDist)
    seq.calculatedRules = [rule]

    samples = resultDist.getRandom(math.ceil(len(seq) / 2))
    if (RESULT_KDE in param):
        resultDist = param[RESULT_KDE]
        samples = param[RESULT_KDE].samples

    printResult(param, baseDistribution, empiricalDist)
    print("Calculation time: {} minutes".format(timer))
    printDistance(resultDist, empiricalDist)
    print("Area between pdf curves: ", distribution.getAreaBetweenDistributions(resultDist, baseDistribution))
    printPerformance(resultDist, samples)
    visualization.showResult(seq, "A", "B", param[RESULT_IDX], baseDistribution, resultDist)
    visualization.showVisualizer(seq)
