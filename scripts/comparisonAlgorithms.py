#!/usr/bin/env python
"""
Plot the result of all algorithms for the same problem.

First problem was inter-arrival distribution Uniform(60, 75) and time-lag Normal(57.01, 6.66). This leads to very
limited overlaps of events.

Second problem was inter-arrival distribution Uniform(5, 55) and time-lag Normal(77.01, 6.66). This leads to many
overlaps of events.

200 events were used for all problems.
"""

import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

# no overlap
true = stats.norm(57.01, 6.66)
lagEm = stats.norm(56.044279071161796, 6.362708854320515)
lp = stats.norm(56.7426443784014, 6.901419693576198)
munkres = stats.norm(57.35554344112395, 6.552604159986489)
ice = stats.norm(56.58205337524414, 6.6947203084439915)

x = np.linspace(25, 95, 10000)
yTrue = true.pdf(x)
yLagEm = lagEm.pdf(x)
yLp = lp.pdf(x)
yMunkres = munkres.pdf(x)
yIce = ice.pdf(x)

plt.plot(x, yTrue, label="True distribution", color="r")
plt.plot(x, yLagEm, label="lagEM", color="b")
plt.plot(x, yLp, label="LpMatcher", color="g")
plt.plot(x, yMunkres, label="MunkresMatcher", color="y")
plt.plot(x, yIce, label="ICE", color="c")
plt.legend()
plt.figure()


# overlap
true = stats.norm(77.01, 6.66)
lagEm = stats.norm(77.69708117865822, 5.688293861445452)
lp = stats.norm(77.18212977062922, 6.157629697647032)
munkres = stats.norm(76.80436865501531, 6.778075732258937)
ice = stats.norm(76.52955200195312, 6.305986299927863)

x = np.linspace(50, 110, 10000)
yTrue = true.pdf(x)
yLagEm = lagEm.pdf(x)
yLp = lp.pdf(x)
yMunkres = munkres.pdf(x)
yIce = ice.pdf(x)

plt.plot(x, yTrue, label="True distribution", color="r")
plt.plot(x, yLagEm, label="lagEM", color="b")
plt.plot(x, yLp, label="LpMatcher", color="g")
plt.plot(x, yMunkres, label="MunkresMatcher", color="y")
plt.plot(x, yIce, label="ICE", color="c")
plt.legend()
plt.figure()


# runtime
barWidth = 0.35

timeLagEm = np.array([118250, 140413, 103702, 152488, 121212])
timeCLagEM = np.array([18860, 12634, 12660, 16462, 15966])
timeMunkres = np.array([313, 337, 332, 365, 571])
timeLp = np.array([1581, 1635, 1622, 1734, 1670, 1616, 1582])
timeIce = np.array([78, 35, 66, 58, 32])

plt.bar(1, timeLagEm.mean() / 1000, barWidth, label="lagEM", color="b")
plt.bar(1.5, timeCLagEM.mean() / 1000, barWidth, label="lagEM in C++", color="r")
plt.bar(2, timeLp.mean() / 1000, barWidth, label="LpMatcher", color="g")
plt.bar(2.5, timeMunkres.mean() / 1000, barWidth, label="MunkresMatcher", color="y")
plt.bar(3, timeIce.mean() / 1000, barWidth, label="ICE", color="c")
plt.legend()
plt.yscale('log')
plt.gca().get_xaxis().set_visible(False)
plt.ylabel("Avg. Runtime in Seconds")
plt.show()


