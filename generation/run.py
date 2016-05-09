#!/usr/bin/env python
""" Automatically generated documentation for run """

import argparse
import logging
import os
import sys

from PySide import QtGui

import generation.entry
from generation.generator import Generator
from generation.visualizer import Visualizer

logging.getLogger().setLevel(logging.DEBUG)

parser = argparse.ArgumentParser()
parser.add_argument("-c", "--count", action="store", type=int, help="Number of sequences to be generated")
parser.add_argument("-n", "--length", action="store", type=int, required=True, help="Length of one sequence")
parser.add_argument("-r", "--rules", action="store", type=str, required=True, help="Path to files containing all rules")
parser.add_argument("-o", "--output", action="store", type=str, help="Pattern for output files")

args = parser.parse_args()
print(args)

if (args.length is None):
    print("Length of sequences not defined")
    print(parser.print_help())
    exit(1)
if (args.rules is None):
    print("Rules not specified")
    print(parser.print_help())
    exit(1)

if (args.output is None):
    print("Output not defined. Printing result to console")
if (args.count is None):
    print("Number of sequences not defined. Assuming 1")
    args.count = 1

entries = generation.entry.loadEntries(args.rules)
rules = []
for entry in entries:
    rules.append(entry.rule)

sequences = Generator() \
    .setSeqLength(args.length) \
    .setEntries(entries) \
    .createSequence(args.count)

if (args.output is None):
    app = QtGui.QApplication(sys.argv)
    i = 0
    for seq in sequences:
        seq.setRules(rules)
        print("Sequence {}".format(str(i)))
        print(str(seq))
        print("\n")

    v = Visualizer()
    v.show()
    v.setSequence(sequences[0])

    sys.exit(app.exec_())

else:
    if not os.path.exists(args.output):
        os.makedirs(args.output)

    i = 0
    for seq in sequences:
        seq.store(args.output + "sequence-" + str(i) + ".seq")
        print(str(seq))
        print("\n")
