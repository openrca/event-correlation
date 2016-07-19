#!/usr/bin/env python
""" Automatically generated documentation for run """

import argparse
import logging
import math
import os

import core.distribution
import core.rule
import generation
import visualization
from algorithms import lpMatcher, lagEM, munkresMatcher, RESULT_MU, RESULT_SIGMA, icpMatcher, RESULT_KDE, RESULT_IDX
from core import sequence, distribution
from core.timer import Timer
from core.distribution import NormalDistribution
from core.performance import RangePerformance, VariancePerformance, StdPerformance, CondProbPerformance, \
    EntropyPerformance
from core.rule import Rule


def printResult(result, distribution, empiricalDist=None):
    msg = "Final parameters:\n"
    for key, value in result.items():
        if (key == RESULT_IDX and value is not None):
            msg += "\t {}: \n{}\n".format(key, value.T)
        else:
            msg += "\t {}: {}\n".format(key, value)
    if (distribution is not None):
        msg += "True parameters:\n\t{}\n".format(str(distribution))
    if (empiricalDist is not None):
        msg += "Empirical parameters:\n\tMu: {}\n\tSigma: {}\n".format(empiricalDist.mu, empiricalDist.sigma)
    logging.info(msg)


def printDistance(dist1, dist2):
    if (dist1 is not None and dist2 is not None):
        logging.info("Distance:\n"
                     "\tKS Test: {}\n"
                     "\tChi2 Test: {}\n".format(core.distribution.kstest(dist1, dist2), 0))


def printPerformance(dist, samples):
    if (dist is not None):
        logging.info("Performance:\n"
                     "\tRange: {}\n"
                     "\tVariance: {}\n"
                     "\tStd: {}\n"
                     "\tCondProd: {}\n"
                     "\tEntropy: {}\n".format(RangePerformance().getValueByDistribution(dist),
                                              VariancePerformance().getValueByDistribution(dist),
                                              StdPerformance().getValueByDistribution(dist),
                                              CondProbPerformance(samples=samples).getValueByDistribution(dist),
                                              EntropyPerformance().getValueByDistribution(dist)))


parser = argparse.ArgumentParser()
parser.add_argument("-r", "--rules", action="store", type=str, help="Path to files containing correct rules")
parser.add_argument("-i", "--input", action="store", type=str, help="Path to file containing sequence")
parser.add_argument("-a", "--algorithm", action="store", type=str, required=True, help="Algorithm to use for alignment")
parser.add_argument("-l", "--length", action="store", type=int, help="Length of to be generated sequence")
parser.add_argument("-c", "--count", action="store", type=int, help="Number of events in generated sequence")
parser.add_argument("-t", "--threshold", action="store", type=float, help="Threshold for convergence", default=0.01)

args = parser.parse_args()
logging.info("Arguments: ".format(args))

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
    logging.info("Loading sequence from {}".format(args.input))
    seq = sequence.loadFromFile(args.input)

logging.info("Processing sequence:\n{}".format(seq))

timer = Timer()
timer.start()
param = None
if (args.algorithm == lpMatcher.LpMatcher.__name__):
    algorithm = lpMatcher.LpMatcher()
    param = algorithm.match(sequence=seq, eventA="A", eventB="B", algorithm=lpMatcher.Method.PULP)

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
    logging.fatal("Unknown algorithm: '{}'".format(args.algorithm))
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
    logging.info("Calculation time: {} minutes".format(timer))
    printDistance(resultDist, empiricalDist)
    logging.info("Area between pdf curves: {}"
                 .format(distribution.getAreaBetweenDistributions(resultDist, baseDistribution)))
    printPerformance(resultDist, samples)
    visualization.showResult(seq, "A", "B", param[RESULT_IDX], baseDistribution, resultDist)
    visualization.showVisualizer(seq)
