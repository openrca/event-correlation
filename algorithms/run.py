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
from generation import symantec

parser = argparse.ArgumentParser()
parser.add_argument("-m", "--method", action="store", type=str, required=True, choices=["gen", "load", "symantec"],
                    help="Method to create sequence.")
parser.add_argument("-i", "--input", action="store", type=str, required=True, help="Path to file containing sequence")
parser.add_argument("-a", "--algorithm", action="store", type=str, required=True, help="Algorithm to use for alignment")

args = parser.parse_args()
logging.info("Arguments: {}".format(args))
# noinspection PyUnresolvedReferences
args.input = os.path.toAbsolutePath(args.input)

seq = None
if (args.method == "gen"):
    logging.info("Creating new sequence")
    seq = generation.createSequences(config=args.input)
if (args.method == "load"):
    logging.info("Loading sequence")
    seq = sequence.loadFromFile(args.input)
if (args.method == "symantec"):
    logging.info("Parsing symantec file")
    seq = symantec.SymantecParser().parse(args.input)

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
    calculatedRules = algorithm.matchAll(sequence=seq, threshold=0.01)

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
