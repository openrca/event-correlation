#!/usr/bin/env python
"""
Compare two distributions and check whether they are correlated or not.
"""
import numpy as np

from core.distribution import NormalDistribution, UniformDistribution, KdeDistribution
import matplotlib.pyplot as plt

from core.performance import RangePerformance, VariancePerformance, StdPerformance, CondProbPerformance, \
    EntropyPerformance

trigger = NormalDistribution(10, 1)
response = UniformDistribution(50, 100)
count = 1000


def showDistributions(trigger, response, ax):
    borders1 = trigger.getCompleteInterval()
    borders2 = response.getCompleteInterval()
    x = np.linspace(min(borders1[0], borders2[0]) - 1, max(borders1[1], borders2[1]) + 1, 500)

    y1 = trigger.getPDFValue(x)
    ax.plot(x, y1, "b", label="Trigger")
    ax.fill_between(x, 0, y1, facecolor='blue', alpha=0.25)

    y2 = response.getPDFValue(x)
    ax.plot(x, y2, "r", label="Response")
    ax.fill_between(x, 0, y2, facecolor='red', alpha=0.25)
    ax.legend()
    ax.set_title("Rvs distribution")


def showDistances(trigger, response, ax):
    delta = np.subtract(trigger, response)
    dist = KdeDistribution(delta)
    # ax.hist(delta)

    x = np.linspace(dist.getCompleteInterval()[0] - 1, dist.getCompleteInterval()[1] + 1, 500)

    y1 = dist.getPDFValue(x)
    ax.plot(x, y1, "b")
    ax.fill_between(x, 0, y1, facecolor='blue', alpha=0.25)
    ax.set_title("Pair-wise distance")


def showPerformanceMeasures(trigger, response, ax):
    delta = np.subtract(trigger, response)
    performance = [RangePerformance().getValueBySamples(delta),
                   VariancePerformance().getValueBySamples(delta),
                   StdPerformance().getValueBySamples(delta),
                   CondProbPerformance().getValueBySamples(delta),
                   EntropyPerformance().getValueBySamples(delta)]
    x = [1, 1.5, 2, 2.5, 3]
    for i in range(len(x)):
        ax.bar(x[i], performance[i], 0.25, color="b", alpha=0.25)

    plt.xticks(np.array(x) + 0.125, ["Range", "Variance", "Std", "CondProb (%)", "Entropy"])
    ax.set_title("Performance")


triggerTimes = trigger.getRandom(count)
responseTimes = response.getRandom(count)

fig, axes = plt.subplots(1, 3)

showDistributions(KdeDistribution(triggerTimes), KdeDistribution(responseTimes), axes[0])
showDistances(triggerTimes, responseTimes, axes[1])
showPerformanceMeasures(triggerTimes, responseTimes, axes[2])

mng = plt.get_current_fig_manager()
mng.resize(*mng.window.maxsize())
plt.show()
