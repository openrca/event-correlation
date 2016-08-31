#!/usr/bin/env python
""" Automatically generated documentation for run """

import argparse
import logging
import os

import generation
import visualization
from algorithms import lpMatcher, lagEM, munkresMatcher, icpMatcher
from core import sequence, distribution
from core.timer import Timer

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
if (args.input is None):
    if (args.rules.startswith("..")):
        args.rules = os.path.join(os.path.dirname(__file__), args.rules)

    seq = generation.createSequences(rules=args.rules, length=args.length, count=args.count)
else:
    logging.info("Loading sequence from {}".format(args.input))
    seq = sequence.loadFromFile(args.input)

logging.info("Processing sequence:\n{}".format(seq))

timer = Timer()
timer.start()
calculatedRules = None
if (args.algorithm == lpMatcher.LpMatcher.__name__):
    algorithm = lpMatcher.LpMatcher()
    calculatedRules = algorithm.matchAll(sequence=seq, algorithm=lpMatcher.Method.PULP)

elif (args.algorithm == munkresMatcher.MunkresMatcher.__name__):
    algorithm = munkresMatcher.MunkresMatcher()
    calculatedRules = algorithm.matchAll(sequence=seq)

elif (args.algorithm == lagEM.lagEM.__name__):
    algorithm = lagEM.lagEM()
    calculatedRules = algorithm.matchAll(sequence=seq, threshold=args.threshold)

elif (args.algorithm == icpMatcher.IcpMatcher.__name__):
    algorithm = icpMatcher.IcpMatcher()
    calculatedRules = algorithm.matchAll(sequence=seq, showVisualization=False, f="confidence")

timer.stop()
logging.info("Calculation time: {} minutes".format(timer))

if (calculatedRules is None):
    logging.fatal("Unknown algorithm: '{}'".format(args.algorithm))
    exit(1)

for rule in calculatedRules:
    resultDist = rule.distributionResponse
    empiricalDist = distribution.getEmpiricalDist(seq, rule.trigger, rule.response)
    baseDist = seq.getBaseDistribution(rule)

    rule.data["Shared Area"] = distribution.getAreaBetweenDistributions(resultDist, baseDist)
    rule.data["Distance KS"] = distribution.kstest(resultDist, empiricalDist)
    rule.data["Distance Chi2"] = 0
    if (baseDist is not None):
        rule.data["True Dist"] = baseDist
    if (empiricalDist is not None):
        rule.data["Empirical Dist"] = empiricalDist

visualization.showVisualizer(seq)
