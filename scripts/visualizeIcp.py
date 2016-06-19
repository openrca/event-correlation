#!/usr/bin/env python
"""
Run the IcpMatcher and visualize the results.

First a curved reference function (b) is defined. Next 60 samples are drawn from the reference function and measurement
noise is added. The measurement is aligned to the reference function by the IcpMatcher. Finally, the reference function,
the noisy measurements and matched references are plotted.
"""

import matplotlib.pyplot as plt
import numpy as np

from algorithms.icpMatcher import IcpMatcher
from core.distribution import NormalDistribution

ang = np.linspace(-np.pi / 2, np.pi / 2, 520)
b = np.array([ang, np.sin(ang)]).T

a = np.array(b, copy=True)
idx = np.random.choice(520, size=60, replace=False)
a = a[idx, :]

noise = NormalDistribution(2, 0.25).getRandom(a.shape[0])
a[:, 0] += noise

init = np.array([5.2, -6.7])
algorithm = IcpMatcher()
algorithm.initPose = init
p = algorithm.compute(a, b)

# plot result
plt.plot(b[:, 0], b[:, 1], c='b', label="Reference")
plt.scatter(a[:, 0], a[:, 1], marker='x', c='r', label="Input")

res = IcpMatcher.transform(p["Offset"], a)
plt.scatter(res[:, 0], res[:, 1], marker='x', c='g', label="Shifted Result")

plt.legend(loc="upper left")
plt.show()
