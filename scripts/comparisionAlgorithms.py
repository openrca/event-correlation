#!/usr/bin/env python
"""
Plot the result of all algorithms for the same problem.

First problem was inter-arrival distribution Uniform(60, 75) and time-lag Normal(57.01, 6.66). This leads to very
limited overlaps of events.

Second problem was inter-arrival distribution Uniform(5, 55) and time-lag Normal(77.01, 6.66). This leads to many
overlaps of events.
"""

from scipy import stats
import numpy as np
import matplotlib.pyplot as plt

true = stats.norm(57.01, 6.66)
lagem = stats.norm(56.044279071161796, 6.362708854320515)
marco = stats.norm(155.01809126474097, 115.83860769346592)
munkres = stats.norm(57.35554344112395, 6.552604159986489)

x = np.linspace(0, 160, 10000)
yTrue = true.pdf(x)
yLagem = lagem.pdf(x)
yMarco = marco.pdf(x)
yMunkres = munkres.pdf(x)

plt.plot(x, yTrue, label="True distribution", color="r")
plt.plot(x, yLagem, label="lagEM", color="b")
plt.plot(x, yMarco, label="MarcoMatcher", color="g")
plt.plot(x, yMunkres, label="MunkresMatcher", color="y")
plt.legend()
plt.show()

plt.figure()
true = stats.norm(77.01, 6.66)
lagem = stats.norm(77.69708117865822, 5.688293861445452)
marco = stats.norm(31.88824156513012, 94.75045018387601)
munkres = stats.norm(76.80436865501531, 6.778075732258937)

x = np.linspace(0, 160, 10000)
yTrue = true.pdf(x)
yLagem = lagem.pdf(x)
yMarco = marco.pdf(x)
yMunkres = munkres.pdf(x)

plt.plot(x, yTrue, label="True distribution", color="r")
plt.plot(x, yLagem, label="lagEM", color="b")
plt.plot(x, yMarco, label="MarcoMatcher", color="g")
plt.plot(x, yMunkres, label="MunkresMatcher", color="y")
plt.legend()
plt.show()
