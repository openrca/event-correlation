#!/usr/bin/env python
"""
Visualize the impact of the initialisation of mu and sigma for lagEM. All results for one mu are plotted in one figure.

Expects one argument with a file template where the sequences are stored. The template has to contain two place holders:
    <MU>:    is replaced by all different mu values
    <SIGMA>: is replaced by all different sigma values
"""

import math
import sys

import matplotlib.pyplot as plt
import numpy as np

from core import sequence
from core.distribution import NormalDistribution

fileTemplate = sys.argv[1]
mu = ["0-42", "42-62", "62-92", "92-112", "112-200"]
sigma = ["1-3.6", "3.6-5.6", "5.6-7.6", "7.6-9.6", "9.6-25"]


def showDistributions(title, trueDist, estimate0, estimate1, estimate2, estimate3, estimate4):
    plt.figure()
    xMin = trueDist.getCompleteInterval()[0]
    xMax = trueDist.getCompleteInterval()[1]
    xMin = min(estimate0.getCompleteInterval()[0], xMin)
    xMax = max(estimate0.getCompleteInterval()[1], xMax)
    xMin = min(estimate1.getCompleteInterval()[0], xMin)
    xMax = max(estimate1.getCompleteInterval()[1], xMax)
    xMin = min(estimate2.getCompleteInterval()[0], xMin)
    xMax = max(estimate2.getCompleteInterval()[1], xMax)
    xMin = min(estimate3.getCompleteInterval()[0], xMin)
    xMax = max(estimate3.getCompleteInterval()[1], xMax)
    xMin = min(estimate4.getCompleteInterval()[0], xMin)
    xMax = max(estimate4.getCompleteInterval()[1], xMax)

    x = np.linspace(xMin, xMax, 500)
    plt.plot(x, trueDist.getPDFValue(x), "b", label="True distribution")
    plt.plot(x, estimate0.getPDFValue(x), "g",
             label="{} ({:.1f}, {:.1f})".format(sigma[0], estimate0.dist.mean(), math.sqrt(estimate0.getVar()())))
    plt.plot(x, estimate0.getPDFValue(x), "r",
             label="{} ({:.1f}, {:.1f})".format(sigma[1], estimate1.dist.mean(), math.sqrt(estimate1.getVar())))
    plt.plot(x, estimate0.getPDFValue(x), "c",
             label="{} ({:.1f}, {:.1f})".format(sigma[2], estimate2.dist.mean(), math.sqrt(estimate2.getVar())))
    plt.plot(x, estimate0.getPDFValue(x), "m",
             label="{} ({:.1f}, {:.1f})".format(sigma[3], estimate3.dist.mean(), math.sqrt(estimate3.getVar())))
    plt.plot(x, estimate0.getPDFValue(x), "y",
             label="{} ({:.1f}, {:.1f})".format(sigma[4], estimate4.dist.mean(), math.sqrt(estimate4.getVar())))
    plt.legend(loc='upper left')
    plt.title(title)
    plt.draw()


def loadDist(mu, sigma):
    return sequence.loadFromFile(fileTemplate.replace("<MU>", mu).replace("<SIGMA>", sigma)).calculatedRules[0] \
        .distribution


trueDist = NormalDistribution(77.01, 6.664082832618454)
dists = [[], [], [], [], []]

for i in range(len(mu)):
    for j in range(len(sigma)):
        dists[i].append(loadDist(mu[i], sigma[j]))
    showDistributions("Mu " + mu[i], trueDist, dists[i][0], dists[i][1], dists[i][2], dists[i][3], dists[i][4])

plt.show()
