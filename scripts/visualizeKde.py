#!/usr/bin/env python
"""
This script has two purposes.

1. Visualization of Kde
    This scripts plots a Kde estimate and 1) compares the pdf values with the correct ones, 2) samples from the
    distribution and 3) plots difference between the estimated cdf and correct ones

2. Show benefits of Kde
    This script shows the difference between a Kde estimate and Normal estimate for various distributions.
"""

import matplotlib.pyplot as plt
import numpy as np
from scipy.stats.distributions import norm

from core import distribution
from core.distribution import KdeDistribution, UniformDistribution, NormalDistribution, ExponentialDistribution

# 1 Visualization of Kde
np.random.seed(0)
xGrid = np.linspace(-4.5, 3.5, 1000)
x = np.concatenate([norm(-1, 1.).rvs(400), norm(1, 0.3).rvs(100)])
dist = KdeDistribution(x)
pdf = dist.getPDFValue(xGrid)

fig, ax = plt.subplots(1, 3, sharex=True, figsize=(13, 3))

pdfTrue = (0.8 * norm(-1, 1).pdf(xGrid) + 0.2 * norm(1, 0.3).pdf(xGrid))
ax[0].plot(xGrid, pdf, color='blue', alpha=0.5, lw=3)
ax[0].fill(xGrid, pdfTrue, ec='gray', fc='gray', alpha=0.4)
ax[0].set_title('Compare pdf values')

samples = dist.getRandom(1000)
ax[1].plot(xGrid, pdf, color='blue', alpha=0.5, lw=3)
ax[1].hist(samples, 50, ec='gray', fc='gray', alpha=0.4, normed=True)
ax[1].set_title('Draw random samples')

cdfTrue = (0.8 * norm(-1, 1).cdf([-5, -4, -3, -2, -1, 0, 1, 2, 3, 4]) +
           0.2 * norm(1, 0.3).cdf([-5, -4, -3, -2, -1, 0, 1, 2, 3, 4]))
print(cdfTrue)

cdf = dist.getCDFValue([-5, -4, -3, -2, -1, 0, 1, 2, 3, 4])
print(cdf)

# noinspection PyTypeChecker
ax[2].plot([-5, -4, -3, -2, -1, 0, 1, 2, 3, 4], cdf - cdfTrue, color='blue', lw=3)
ax[2].set_title('Distance between true cdf and calculated cdf')
plt.show()

# 2. Benefits of Kde
x = np.linspace(0, 10, 1000)
trueDist = NormalDistribution(5.01, 1.5)
kdeDist = KdeDistribution(
    [5.9259, 5.0249, 8.0681, 3.4785, 3.4607, 2.7296, 3.9944, 4.9824, 6.302, 6.3485, 3.165, 5.7351, 6.7904, 5.5762,
     4.538, 5.7765, 2.7071, 5.2868, 5.8443, 3.9802, 5.3272, 6.006, 5.3421, 3.1916, 4.3714, 6.6785, 3.2838, 5.4728,
     3.7137, 3.2563, 5.9146, 7.7886, 7.1684, 4.9038, 5.1424, 3.69, 5.2851, 7.2171, 5.0286, 3.1016, 5.4904, 4.6723,
     3.5014, 4.1787, 6.1515, 7.0393, 4.3286, 2.7126, 4.6876, 5.5366, 6.727, 4.551, 5.3195, 4.8563, 6.5825, 5.6579,
     4.7545, 4.7822, 6.213, 4.6029, 2.7199, 3.2628, 4.5341, 4.9195, 4.0556, 6.9209, 4.772, 2.8476, 6.2138, 4.0185,
     7.409, 3.1998, 2.9726, 6.4394, 4.1606, 4.5226, 4.7813, 5.5894, 6.469, 6.0271, 3.156, 5.8009, 4.9298, 5.4745,
     6.5971, 5.8339, 4.0871, 4.2908, 4.9553, 4.6765, 4.4929, 5.6421, 7.1592, 5.4849, 6.9298, 4.5134, 3.1468, 4.3647])
normalDist = NormalDistribution(5.013421410133262, 1.2946318912766)

print("True distribution is Normal distribution")
print("Shared area for Normal distribution: ", distribution.getAreaBetweenDistributions(trueDist, normalDist))
print("Shared area for Kde distribution: ", distribution.getAreaBetweenDistributions(trueDist, kdeDist))
print("Relative entropy for Normal distribution: ", distribution.getRelativeEntropy(trueDist, normalDist))
print("Relative entropy for Kde distribution: ", distribution.getRelativeEntropy(trueDist, kdeDist))

plt.plot(x, trueDist.getPDFValue(x), color="r", label="True distribution")
plt.plot(x, normalDist.getPDFValue(x), color="b", label="Normal distribution")
plt.plot(x, kdeDist.getPDFValue(x), color="g", label="Kde distribution")
plt.title("Normal distribution")
plt.legend()
plt.show()

x = np.linspace(3, 12, 1000)
trueDist = UniformDistribution(5, 10)
kdeDist = KdeDistribution(
    [7.1036, 5.4399, 7.2933, 7.8562, 8.6774, 5.0413, 6.6801, 7.8481, 6.3956, 7.8588, 9.056, 5.5733, 6.8569, 8.1246,
     7.9401, 5.6402, 8.0831, 9.1643, 9.8654, 7.0268, 6.5733, 9.0658, 9.1412, 7.6359, 7.7627, 6.2847, 7.4184, 9.3168,
     6.5808, 5.1225, 6.5798, 7.028, 8.1771, 7.4708, 8.0322, 6.779, 6.4643, 9.4948, 5.2301, 9.5652, 7.6179, 7.3952,
     9.806, 5.5997, 6.0012, 8.6953, 6.407, 9.0033, 6.1444, 7.7224, 5.2776, 8.1565, 7.7607, 9.0577, 9.0729, 8.8478,
     9.1855, 8.2948, 6.4959, 5.5056, 8.7751, 8.8484, 9.1587, 6.7644, 6.1248, 9.9632, 9.099, 7.0455, 9.9518, 5.5176,
     5.613, 5.5994, 7.4866, 9.3597, 8.5692, 6.3792, 5.3595, 6.679, 7.9058, 6.669, 8.2082, 6.5063, 8.0021, 6.4516, 6.132,
     5.7746, 6.4881, 7.2319, 8.6818, 6.4934, 5.1316, 7.9194, 9.0235, 8.0029, 5.6738, 9.8622, 6.1441, 5.9018, 9.4573,
     5.7889])
normalDist = NormalDistribution(7.431321324171027, 1.4511659410549063)

print("\nTrue distribution is Uniform distribution")
print("Shared area for Normal distribution: ", distribution.getAreaBetweenDistributions(trueDist, normalDist))
print("Shared area for Kde distribution: ", distribution.getAreaBetweenDistributions(trueDist, kdeDist))
print("Relative entropy for Normal distribution: ", distribution.getRelativeEntropy(trueDist, normalDist))
print("Relative entropy for Kde distribution: ", distribution.getRelativeEntropy(trueDist, kdeDist))

plt.plot(x, trueDist.getPDFValue(x), color="r", label="True distribution")
plt.plot(x, normalDist.getPDFValue(x), color="b", label="Normal distribution")
plt.plot(x, kdeDist.getPDFValue(x), color="g", label="Kde distribution")
plt.title("Uniform distribution")
plt.legend()
plt.show()

x = np.linspace(-5, 35, 1000)
trueDist = ExponentialDistribution(2, 10)
kdeDist = KdeDistribution(
    [29.0636, 23.7378, 14.4818, 18.419, 6.0431, 3.3395, 12.2812, 15.6998, 9.9592, 4.9988, 11.2077, 25.8959, 22.7192,
     19.4778, 17.7977, 4.1812, 5.1253, 3.203, 4.3251, 12.7011, 15.9507, 15.0248, 15.9752, 8.4376, 18.9881, 12.8122,
     7.4235, 9.5878, 3.3641, 3.8647, 7.9739, 9.0641, 6.827, 17.2279, 15.8699, 14.3722, 2.7732, 2.1239, 16.7671, 27.555,
     29.1603, 17.6583, 11.5634, 9.5922, 19.1209, 14.168, 18.8858, 10.7597, 13.1935, 15.7445, 14.5384, 2.3002, 2.6062,
     4.2566, 9.1554, 17.8881, 7.3633, 10.7905, 3.2125, 2.7131, 8.8323, 5.5761, 9.3102, 9.9232, 19.4521, 18.4323, 7.806,
     11.9186, 22.004, 16.3168, 13.3261, 10.6107, 6.0937, 7.3862, 2.8321, 8.9818, 14.3169, 15.4862, 8.2905, 3.2816,
     2.0763, 7.9852, 6.7399, 10.177, 13.7641, 19.9483, 19.297, 16.5613, 11.3849, 24.4364, 20.6557, 23.4644, 23.5463,
     15.1912, 18.1363, 17.1629, 4.2176, 3.5967, 24.6061])
normalDist = NormalDistribution(12.469051933513562, 6.907956521247542)

print("\nTrue distribution is Exponential distribution")
print("Shared area for Normal distribution: ", distribution.getAreaBetweenDistributions(trueDist, normalDist))
print("Shared area for Kde distribution: ", distribution.getAreaBetweenDistributions(trueDist, kdeDist))
print("Relative entropy for Normal distribution: ", distribution.getRelativeEntropy(trueDist, normalDist))
print("Relative entropy for Kde distribution: ", distribution.getRelativeEntropy(trueDist, kdeDist))

plt.plot(x, trueDist.getPDFValue(x), color="r", label="True distribution")
plt.plot(x, normalDist.getPDFValue(x), color="b", label="Normal distribution")
plt.plot(x, kdeDist.getPDFValue(x), color="g", label="Kde distribution")
plt.title("Exponential distribution")
plt.legend()
plt.show()

# shared areas
barWidth = 0.35
plt.bar(1, 0.926027500905, barWidth, color="b", label="Normal distribution")
plt.bar(1.4, 0.962336154809, barWidth, color="r", label="Kde distribution")
plt.bar(2, 0.802804643457, barWidth, color="b")
plt.bar(2.4, 0.896111931788, barWidth, color="r")
plt.bar(3, 0.673843180266, barWidth, color="b")
plt.bar(3.4, 0.734559815708, barWidth, color="r")

plt.xticks([1.35, 2.35, 3.35], ["Normal", "Uniform", "Exponential"])
plt.legend()
plt.ylabel("Shared areas of estimated pdfs")
plt.show()

# relative entropy
barWidth = 0.35
plt.bar(1, 0.0183126101663, barWidth, color="b", label="Normal distribution")
plt.bar(1.4, 0.0314108004155, barWidth, color="r", label="Kde distribution")
plt.bar(2, 0.167637283631, barWidth, color="b")
plt.bar(2.4, 0.101927070935, barWidth, color="r")
plt.bar(3, 0.480865966885, barWidth, color="b")
plt.bar(3.4, 0.540199081816, barWidth, color="r")

plt.xticks([1.35, 2.35, 3.35], ["Normal", "Uniform", "Exponential"])
plt.legend()
plt.ylabel("Relative entropy of estimated pdfs")
plt.show()
