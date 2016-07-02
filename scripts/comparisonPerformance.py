#!/usr/bin/env python
"""
Compare different Performance Measures for three problems

First problem is inter-arrival distribution Uniform(5, 15) and time-lag Normal(7, 2) and success of 1.
Second problem is like the first-one except that trigger and response success were 0.95.
Third problem is inter-arrival distribution of 'A' as Normal(8, 1) and inter-arrival distribution of 'B' as
Uniform(10, 30). 'A' and 'B' were independent of each other.

100 Events were used for each problem.
"""

import matplotlib.pyplot as plt


barWidth = 0.35
plt.bar(1.0, 29.996992529782602, barWidth, color="b", label="Uncorrelated")
plt.bar(1.4, 14.820276959142337, barWidth, color="r", label="Correlated 95%")
plt.bar(1.8, 13.819114456248048, barWidth, color="g", label="Correlated 100%")

plt.bar(2.5, 41.30677346593584, barWidth, color="b")
plt.bar(2.9, 3.8916081254698893, barWidth, color="r")
plt.bar(3.3, 3.771603239918598, barWidth, color="g")

plt.bar(4.0, 6.427034577932178, barWidth, color="b")
plt.bar(4.4, 1.9727159261966456, barWidth, color="r")
plt.bar(4.8, 1.9420615952947007, barWidth, color="g")

plt.bar(5.5, 4.0521578856842384, barWidth, color="b")
plt.bar(5.9, 14.482403262590507, barWidth, color="r")
plt.bar(6.3, 14.382774384244792, barWidth, color="g")

plt.bar(7.0, 3.2834936422176018, barWidth, color="b")
plt.bar(7.4, 2.180808041879395, barWidth, color="r")
plt.bar(7.8, 2.1683330114735204, barWidth, color="g")

plt.xticks([1.55, 3.05, 4.55, 6.05, 7.55], ["Range", "Variance", "Std", "CondProb (%)", "Entropy"])
plt.legend()
plt.xlim((0.75, 8.4))
plt.show()
