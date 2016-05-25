#!/usr/bin/env python
"""
Visualize the impact of the initialisation of mu for lagEM mu was initialized as mu = 0, 1, 2, ..., 199

Expects one argument with the path to the file containing all values
"""

import sys

import matplotlib.pyplot as plt

initMu = []
calcMu = []
calcSigma = []
likelihood = []

fileName = sys.argv[1]
with open(fileName) as file:
    for line in file:
        tokens = line.split(" ")
        initMu.append(tokens[0])
        calcMu.append(tokens[1])
        calcSigma.append(tokens[2])
        likelihood.append(tokens[3])

plt.subplot(311)
plt.title("Calculated Mu")
plt.plot(initMu, calcMu, label="Calculated mu")
plt.plot(initMu, [77.01] * len(initMu), label="Real mu")
plt.legend(loc="upper left")

plt.subplot(312)
plt.title("Calculated Sigma")
plt.plot(initMu, calcSigma, label="Calculated sigma")
plt.plot(initMu, [6.664082832618454] * len(initMu), label="Real sigma")
plt.legend(loc="upper left")

plt.subplot(313)
plt.title("Likelihood")
plt.yscale('log')
plt.plot(initMu, likelihood)

plt.show()
