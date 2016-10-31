#!/usr/bin/env python
""" Automatically generated documentation for run """

import argparse
import logging
import os

import provider
import visualization
from algorithms import lpMatcher, lagEM, munkresMatcher, icpMatcher
from core import sequence, distribution
from core.timer import Timer
from provider import symantec, generator

parser = argparse.ArgumentParser()
parser.add_argument("-m", "--method", action="store", type=str, required=True, choices=provider.CHOICES,
                    help="Method to create sequence.")
parser.add_argument("-i", "--input", action="store", type=str, required=True, help="Path to file containing sequence")
parser.add_argument("-a", "--algorithm", action="store", type=str, required=True, help="Algorithm to use for alignment")
parser.add_argument("-t", "--trigger", action="store", type=str, required=False,
                    help="Match only given trigger and response")
parser.add_argument("-r", "--response", action="store", type=str, required=False,
                    help="Match only given trigger and response")

args = parser.parse_args()
logging.info("Arguments: {}".format(args))
# noinspection PyUnresolvedReferences
args.input = os.path.toAbsolutePath(args.input)

trigger = args.trigger
response = args.response
if (trigger is None and response is not None):
    logging.fatal('No trigger defined. Please add a trigger or remove response. {}'.format(parser.format_help()))
    exit()
if (trigger is not None and response is None):
    logging.fatal('No response defined. Please add a response or remove trigger. {}'.format(parser.format_help()))
    exit()

seq = None
if (args.method == provider.GENERATE):
    logging.info("Creating new sequence")
    seq = generator.Generator().create(args.input)
if (args.method == provider.LOAD):
    logging.info("Loading sequence")
    seq = sequence.loadFromFile(args.input)
if (args.method == provider.SYMANTEC):
    logging.info("Parsing symantec file")
    if (trigger is not None and response is not None):
        seq = symantec.SymantecParser().create(args.input, whitelist=[trigger, response], normalization=100)
    else:
        seq = symantec.SymantecParser().create(args.input, normalization=100)

logging.info("Processing sequence:\n{}".format(seq))

timer = Timer()
timer.start()
algorithm = None
kwargs = {}
if (args.algorithm == lpMatcher.LpMatcher.__name__):
    algorithm = lpMatcher.LpMatcher()
    kwargs["algorithm"] = lpMatcher.Method.PULP

elif (args.algorithm == munkresMatcher.MunkresMatcher.__name__):
    algorithm = munkresMatcher.MunkresMatcher()

elif (args.algorithm == lagEM.lagEM.__name__):
    algorithm = lagEM.lagEM()
    kwargs["threshold"] = 0.01

elif (args.algorithm == icpMatcher.IcpMatcher.__name__):
    algorithm = icpMatcher.IcpMatcher()
    kwargs["showVisualization"] = False
    kwargs["f"] = "confidence"

if (algorithm is None):
    logging.fatal("Unknown algorithm: '{}'".format(args.algorithm))
    exit(1)

if (trigger is None and response is None):
    calculatedRules = algorithm.matchAll(sequence=seq, **kwargs)
else:
    calculatedRules = [algorithm.match(seq, trigger, response, **kwargs)[0]]

timer.stop()
logging.info("Calculation time: {} minutes".format(timer))

for rule in calculatedRules:
    seq.calculatedRules.append(rule)
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
