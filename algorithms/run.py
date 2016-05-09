#!/usr/bin/env python
""" Automatically generated documentation for run """

import argparse
import sys

import matplotlib.pyplot as plt
import numpy as np
from PySide import QtGui

import core.distribution
import generation.entry
from algorithms import munkresAssign, lagEM
from core import sequence
from core.distribution import NormalDistribution
from core.rule import Rule
from generation.generator import Generator
from generation.visualizer import Visualizer


def printResult(result, distributions):
    print("Final parameters:")
    for key, value in result.items():
        print("\t {}: {}".format(key, value))
    if (distributions is not None):
        print("True parameters:")
        for d in distributions:
            print("\t {}".format(str(d)))


def printDistance(dist1, dist2):
    print("Distance:")
    print("\tKS Test: " + str(core.distribution.kstest(dist1, dist2)))
    print("\tChi2 Test: " + str(core.distribution.chi2test(dist1, dist2)))


def showDistributions(dist1, dist2):
    borders1 = dist1.dist.interval(0.99)
    borders2 = dist2.dist.interval(0.99)
    x = np.linspace(min(borders1[0], borders2[0]), max(borders1[1], borders2[1]), 500)
    plt.plot(x, dist1.dist.pdf(x), "b", label="Estimated distribution")
    plt.plot(x, dist2.dist.pdf(x), "r", label="True distribution")
    plt.legend()
    plt.show()


parser = argparse.ArgumentParser()
parser.add_argument("-r", "--rules", action="store", type=str, help="Path to files containing correct rules")
parser.add_argument("-i", "--input", action="store", type=str, help="Path to files containing sequences")
parser.add_argument("-a", "--algorithm", action="store", type=str, required=True, help="Algorithm to use for alignment")
parser.add_argument("-l", "--length", action="store", type=int, help="Length of to be generated sequence")

args = parser.parse_args()
print(args)

seq = None
baseDistributions = []
if (args.input is None):
    if (args.rules is None):
        print("Neither rules nor input specified. Please provide at least one")
        exit(1)
    else:
        if (args.length is None):
            args.length = 20

        print("Creating new sequence from {} with length {}".format(args.rules, args.length))
        entries = generation.entry.loadEntries(args.rules)
        for entry in entries:
            baseDistributions.append(entry.rule.getDistribution())

        seq = Generator() \
            .setSeqLength(args.length) \
            .setEntries(entries) \
            .createSequence(1)[0]

else:
    print("Loading sequence from {}".format(args.input))
    seq = sequence.loadFromFile(args.input)

print("Processing sequence:")
print(str(seq))
app = QtGui.QApplication(sys.argv)

if (args.algorithm == 'munkresAssign'):
    munkresAssign.munkresAssign(seq, "A", "B")
elif (args.algorithm == 'lagEM'):
    algorithm = lagEM.lagEM()
    param = algorithm.match(sequence=seq, eventA="A", eventB="B", threshold=0.01)

    dist = NormalDistribution(param["Mu"], param["Sigma"])
    rule = Rule("A", "B", dist)
    seq.setRules([rule])

    printResult(param, baseDistributions)
    printDistance(dist, baseDistributions[0])
    showDistributions(dist, baseDistributions[0])
    v = Visualizer()
    v.show()
    v.setSequence(seq)
else:
    print("Unknown algorithm: '{}'".format(args.algorithm))
    exit(1)
sys.exit(app.exec_())
