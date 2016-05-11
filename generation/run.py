#!/usr/bin/env python
""" Automatically generated documentation for run """
import os

from generation import createSequences, args

sequences = createSequences()
i = 0
for seq in sequences:
    if (args.output is None):
        print("Sequence {}".format(str(i)))
        print(str(seq))
        print("\n")
    else:
        if not os.path.exists(args.output):
            os.makedirs(args.output)

        seq.store(args.output + "sequence-" + str(i) + ".seq")
        print(str(seq))
        print("\n")
    i += 1
