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

mu = ["0-42", "42-62", "62-92", "92-112", "112-200"]
sigma = ["1-3.6", "3.6-5.6", "5.6-7.6", "7.6-9.6", "9.6-25"]


scenario1 = [NormalDistribution(48.0, 7.3), NormalDistribution(47.2, 7.1), NormalDistribution(50.4, 6.1),
             NormalDistribution(49.8, 7.2), NormalDistribution(48.0, 7.4)]
scenario2 = [NormalDistribution(47.9, 7.0), NormalDistribution(48.6, 7.6), NormalDistribution(49.0, 8.1),
             NormalDistribution(47.7, 7.6), NormalDistribution(48.7, 6.8)]
scenario3 = [NormalDistribution(76.7, 6.6), NormalDistribution(76.0, 6.4), NormalDistribution(76.6, 6.9),
             NormalDistribution(77.7, 7.4), NormalDistribution(76.9, 7.0)]
scenario4 = [NormalDistribution(105.1, 7.0), NormalDistribution(106.0, 6.5), NormalDistribution(105.3, 7.8),
             NormalDistribution(104.4, 6.5), NormalDistribution(105.3, 7.4)]
scenario5 = [NormalDistribution(132.4, 9.2), NormalDistribution(118.7, 7.3), NormalDistribution(111.3, 7.0),
             NormalDistribution(113.1, 7.9), NormalDistribution(105.3, 6.5)]


def showDistributions(trueDist, estimate0, estimate1, estimate2, estimate3, estimate4):
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
    plt.rc('axes', labelsize=14)
    plt.plot(x, trueDist.getPDFValue(x), "b", linewidth=1.2, label="True distribution")
    plt.plot(x, estimate0.getPDFValue(x), "g", linewidth=1.2,
             label="{}    $\mathcal{{N}}$({:.1f}, {:.1f})".format(sigma[0], estimate0._dist.mean(),
                                                                  math.sqrt(estimate0.getVar())))
    plt.plot(x, estimate0.getPDFValue(x), "r", linewidth=1.2,
             label="{} $\mathcal{{N}}$({:.1f}, {:.1f})".format(sigma[1], estimate1._dist.mean(),
                                                               math.sqrt(estimate1.getVar())))
    plt.plot(x, estimate0.getPDFValue(x), "c", linewidth=1.2,
             label="{} $\mathcal{{N}}$({:.1f}, {:.1f})".format(sigma[2], estimate2._dist.mean(),
                                                               math.sqrt(estimate2.getVar())))
    plt.plot(x, estimate0.getPDFValue(x), "m", linewidth=1.2,
             label="{} $\mathcal{{N}}$({:.1f}, {:.1f})".format(sigma[3], estimate3._dist.mean(),
                                                               math.sqrt(estimate3.getVar())))
    plt.plot(x, estimate0.getPDFValue(x), "y", linewidth=1.2,
             label="{}  $\mathcal{{N}}$({:.1f}, {:.1f})".format(sigma[4], estimate4._dist.mean(),
                                                                math.sqrt(estimate4.getVar())))
    plt.legend(loc='upper left')
    plt.xlabel("Time Lag")
    plt.ylabel("Probability Density")
    plt.draw()


trueDist = NormalDistribution(77.01, 6.664082832618454)
dists = [scenario1, scenario2, scenario3, scenario4, scenario5]

for i in range(len(mu)):
    showDistributions(trueDist, dists[i][0], dists[i][1], dists[i][2], dists[i][3], dists[i][4])

plt.show()
