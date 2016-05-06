#!/usr/bin/env python
""" Automatically generated documentation for run """

import argparse
import sys

from PySide import QtGui

import core.distribution
import generation
from algorithms import munkresAssign, lagEM
from core import sequence
from core.distribution import NormalDistribution
from core.rule import Rule
from generation.generator import Generator
from generation.visualizer import Visualizer


def printResult(result, rules):
    print("Final parameters:")
    for key, value in result:
        print("\t {}: {}".format(key, value))
    if (rules is not None):
        print("True parameters:")
        for r in rules:
            print("\t {}".format(str(r.getDistribution())))


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
        entries = generation.loadEntries(args.rules)
        for entry in entries:
            baseDistributions.append(entry[0].getDistribution())

        seq = Generator() \
            .setSeqLength(args.length) \
            .setRules(entries) \
            .createSequence(1)[0]

else:
    print("Loading sequence from {}".format(args.input))
    seq = sequence.loadFromFile(args.input)

print("Processing sequence:")
print(str(seq))

if (args.algorithm == 'munkresAssign'):
    munkresAssign.munkresAssign(seq, "A", "B")
elif (args.algorithm == 'lagEM'):
    algorithm = lagEM.lagEM()
    mu, sigma = algorithm.match(sequence=seq, eventA="A", eventB="B", threshold=0.01)
    print("Mu: {}".format(mu))
    print("Sigma: {}".format(sigma))

    dist = NormalDistribution(mu, sigma)
    rule = Rule("A", "B", dist)
    seq.setRules([rule])

    print("Distance:")
    print("\tKS Test: " + str(core.distribution.kstest(dist, baseDistributions[0])))
    print("\t Chi2 Test: " + str(core.distribution.chi2test(dist, baseDistributions[0])))

    app = QtGui.QApplication(sys.argv)
    v = Visualizer()
    v.show()
    v.setSequence(seq)
    sys.exit(app.exec_())
else:
    print("Unknown algorithm: '{}'".format(args.algorithm))
    exit(1)
