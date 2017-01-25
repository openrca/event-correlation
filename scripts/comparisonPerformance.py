#!/usr/bin/env python
import matplotlib.pyplot as plt
import numpy as np

ind = np.arange(4)
width = 0.2
opacity = 0.9

# runtime
fig = plt.figure()
ax = fig.add_subplot(111)
rects1 = ax.bar(ind, [4.233333333, 1.525666667, 2.981, 38.246], width,
                color='c', alpha=opacity)
rects2 = ax.bar(ind + width, [23.769666667, 4.081666667, 3.31, 58.803333333], width,
                color='g', alpha=opacity)
rects3 = ax.bar(ind + 2 * width, [971.304333333, 2407.909, 1605.804666667, 15512.0006667], width,
                color='b', alpha=opacity)

# axes and labels
ax.set_xlim(-width, len(ind) + width)
ax.set_ylabel('Seconds')
xTickMarks = ['Scenario' + str(i) for i in range(1, 5)]
ax.set_xticks(ind + width)
xTickNames = ax.set_xticklabels(xTickMarks)
plt.setp(xTickNames, rotation=45, fontsize=10)
ax.legend((rects1[0], rects2[0], rects3[0]), ('ICP', 'LpMatcher', 'lagEM'), loc='best')
plt.yscale('log')

# memory
fig = plt.figure()
ax = fig.add_subplot(111)
rects1 = ax.bar(ind, [93.506510667, 93.404948, 93.516927, 94.756510333], width,
                color='c', alpha=opacity)
rects2 = ax.bar(ind + width, [268.868489333, 120.430989667, 117.119791667, 269.135416667], width,
                color='g', alpha=opacity)
rects3 = ax.bar(ind + 2 * width, [95.865885333, 93.882241333, 115.217656333, 95.985677333], width,
                color='b', alpha=opacity)

# axes and labels
ax.set_xlim(-width, len(ind) + width)
ax.set_ylabel('MB')
xTickMarks = ['Scenario' + str(i) for i in range(1, 5)]
ax.set_xticks(ind + width)
xTickNames = ax.set_xticklabels(xTickMarks)
plt.setp(xTickNames, rotation=45, fontsize=10)
ax.legend((rects1[0], rects2[0], rects3[0]), ('ICP', 'LpMatcher', 'lagEM'), loc='best')
plt.show()
