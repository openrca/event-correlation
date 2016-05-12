import argparse
import logging

from generation import entry
from generation.generator import Generator

logging.getLogger().setLevel(logging.DEBUG)

parser = argparse.ArgumentParser()
parser.add_argument("-c", "--count", action="store", type=int, help="Number of sequences to be generated")
parser.add_argument("-n", "--length", action="store", type=int, required=True, help="Length of one sequence")
parser.add_argument("-r", "--rules", action="store", type=str, required=True, help="Path to files containing all rules")
parser.add_argument("-o", "--output", action="store", type=str, help="Pattern for output files")


def createSequences():
    args = parser.parse_args()
    print("Creating sequence based on " + str(args))

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

    entries = entry.loadEntries(args.rules)
    rules = []
    for e in entries:
        rules.append(e.rule)

    sequences = Generator() \
        .setSeqLength(args.length) \
        .setEntries(entries) \
        .createSequence(args.count)
    for seq in sequences:
        seq.rules = rules

    return sequences
