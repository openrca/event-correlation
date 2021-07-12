#!/usr/bin/env python
""" Automatically generated documentation for run """

import argparse
import json
import logging
import os
import sys

from PySide2.QtWidgets import QApplication

import provider
from algorithms import lpMatcher, lagEM, munkresMatcher, ice
from core import sequence, distribution
from core.performance import EnergyDistance
from core.timer import Timer
from provider import symantec, generator, hdPrinter
from visualization.visualizer import Visualizer

parser = argparse.ArgumentParser()
parser.add_argument("-m", "--method", action="store", type=str, required=True, choices=provider.CHOICES,
                    help="Method to create sequence.")
parser.add_argument("-i", "--input", action="store", type=str, required=True, help="Path to file containing sequence")
parser.add_argument("-a", "--algorithm", action="store", type=str, required=True, help="Algorithm to use for alignment")
parser.add_argument("-t", "--trigger", action="store", type=str, required=False,
                    help="Match only given trigger and response")
parser.add_argument("-r", "--response", action="store", type=str, required=False,
                    help="Match only given trigger and response")
parser.add_argument("-d", "--distributions", action="store", type=str, required=False,
                    help="Path to file containing true empirical distributions")

args = parser.parse_args()
logging.info("Arguments: {}".format(args))
# noinspection PyUnresolvedReferences
args.input = os.path.toAbsolutePath(args.input)
# noinspection PyUnresolvedReferences
args.distributions = os.path.toAbsolutePath(args.distributions)

trigger = args.trigger
response = args.response
if (trigger is None and response is not None):
    logging.fatal('No trigger defined. Please add a trigger or remove response. {}'.format(parser.format_help()))
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
if (args.method == provider.PRINTER):
    logging.info("Parsing HD printer file")
    if (trigger is not None and response is not None):
        seq = hdPrinter.HDPrinterParser().create(args.input, whitelist=[trigger, response], normalization=100)
    else:
        seq = hdPrinter.HDPrinterParser().create(args.input, normalization=100)
logging.info("Processing sequence:\n{}".format(seq))

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
    kwargs["enforceNormal"] = True

elif (args.algorithm == ice.ICE.__name__):
    algorithm = ice.ICE()
    kwargs["showVisualization"] = False
    kwargs["f"] = "confidence"

if (algorithm is None):
    logging.fatal("Unknown algorithm: '{}'".format(args.algorithm))
    exit(1)

timer = Timer()
timer.start()
if (len(seq.calculatedRules) > 0):
    calculatedRules = seq.calculatedRules
    seq.calculatedRules = []
elif (trigger is None):
    calculatedRules = algorithm.matchAll(seq, **kwargs)
elif (response is None):
    calculatedRules = algorithm.matchTransitive(seq, trigger, **kwargs)
else:
    calculatedRules = [algorithm.match(seq, trigger, response, **kwargs)[0]]
timer.stop()
logging.info("Calculation time: {} minutes".format(timer))

knownEmpiricalDists = None
if (args.distributions is not None):
    with open(args.distributions, "r") as file:
        knownEmpiricalDists = json.loads("".join(file.readlines()))

for rule in calculatedRules:
    seq.calculatedRules.append(rule)

    baseDist = seq.getBaseDistribution(rule.trigger, rule.response)
    if (baseDist is not None):
        rule.data["True Dist"] = baseDist

    empiricalDist = distribution.getEmpiricalDist(seq, rule.trigger, rule.response, knownEmpiricalDists)
    if (empiricalDist is not None):
        rule.data["Empirical Dist"] = empiricalDist
        samples = rule.distributionResponse.samples if (hasattr(rule.distributionResponse, 'samples')) else\
            rule.distributionResponse.getRandom(len(empiricalDist.samples))
        rule.data["Distance to Empirical"] = EnergyDistance().compute(samples, empiricalDist.samples)

app = QApplication(sys.argv)
v = Visualizer()
v.setSequence(seq)
if (trigger is not None and response is None):
    v.setDependencyRoot(trigger)

v.show()
sys.exit(app.exec_())
