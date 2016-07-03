#!/usr/bin/env python
"""
Compare different Performance Measures for three problems

First problem is inter-arrival distribution of 'A' as Normal(8, 1) and inter-arrival distribution of 'B' as
    Uniform(10, 30). 'A' and 'B' were independent of each other.
Second problem is inter-arrival distribution Uniform(5, 15) and time-lag Normal(7, 2) and success of 1.
Third problem is like the first-one except that trigger and response success were 0.95.
Fourth problem is inter-arrival distribution Uniform(60, 75) and time-lag Normal(57.01, 6.66) and trigger, response
    success of 0.95.
Fifth problem is inter-arrival distribution of 'A' as Uniform(0, 50) and inter-arrival distribution of 'B' as
    Uniform(10, 100). 'A' and 'B' were independent of each other.

100 Events were used for each problem.
"""

import matplotlib.pyplot as plt

barWidth = 0.25
plt.bar(1.0, 29.996992529782602, barWidth, color="b", label="Uncorrelated")
plt.bar(1.3, 14.820276959142337, barWidth, color="r", label="Correlated I 95% ")
plt.bar(1.6, 13.819114456248048, barWidth, color="g", label="Correlated I 100%")
plt.bar(1.9, 42.56123056335491, barWidth, color="c", label="Correlated II 95%")
plt.bar(2.2, 3112.191577537384, barWidth, color="m", label="Uncorrelated II")

plt.bar(2.9, 41.30677346593584, barWidth, color="b")
plt.bar(3.2, 3.8916081254698893, barWidth, color="r")
plt.bar(3.5, 3.771603239918598, barWidth, color="g")
plt.bar(3.8, 44.69834203114192, barWidth, color="c")
plt.bar(4.1, 837192.8868330343, barWidth, color="m")

plt.bar(4.8, 6.427034577932178, barWidth, color="b")
plt.bar(5.1, 1.9727159261966456, barWidth, color="r")
plt.bar(5.4, 1.9420615952947007, barWidth, color="g")
plt.bar(5.7, 6.685681867329758, barWidth, color="c")
plt.bar(6.0, 914.9824516530546, barWidth, color="m")

plt.bar(6.7, 4.0521578856842384, barWidth, color="b")
plt.bar(7.0, 14.482403262590507, barWidth, color="r")
plt.bar(7.3, 14.382774384244792, barWidth, color="g")
plt.bar(7.6, 4.218218322159476, barWidth, color="c")
plt.bar(7.9, 0.029351750354985836, barWidth, color="m")

plt.bar(8.6, 3.2834936422176018, barWidth, color="b")
plt.bar(8.9, 2.180808041879395, barWidth, color="r")
plt.bar(9.2, 2.1683330114735204, barWidth, color="g")
plt.bar(9.5, 3.328313164602277, barWidth, color="c")
plt.bar(9.8, 8.019656080389547, barWidth, color="m")

plt.xticks([1.6, 3.5, 5.4, 7.3, 9.2], ["Range", "Variance", "Std", "CondProb (%)", "Entropy"])
plt.legend()
plt.xlim((0.75, 10.3))
plt.ylim((0, 70))
plt.show()
