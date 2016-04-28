#!/usr/bin/env python
""" Automatically generated documentation for run """

import argparse
import logging
import sys

from PySide import QtGui

import generation
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

entries = generation.loadEntries(args.rules)

sequences = Generator() \
    .setSeqLength(args.length) \
    .setRules(entries) \
    .createSequence(args.count)

if (args.output is None):
    for i in range(0, args.count):
        print("Sequence {}".format(str(i)))
        print(str(sequences[i]))
        print("\n")

    app = QtGui.QApplication(sys.argv)

    v = Visualizer()
    v.show()
    v.setSequence(sequences[0])

    sys.exit(app.exec_())

else:
    raise NotImplementedError("Not implemented yet")
