#!/usr/bin/env python
import matplotlib.pyplot as plt
import numpy as np

ind = np.arange(6)
width = 0.35
opacity = 0.9

# memory
fig = plt.figure()
ax = fig.add_subplot(111)
rects1 = ax.bar(ind, 1 - np.array([
    0.99970217206124, 0.9977980690759589, 0.9977980690759589, 0.9988978210770524, 0.9988978210770523,
    0.9946879366150463]), width, color='r', alpha=opacity)
rects2 = ax.bar(ind + width, 1 - np.array([
    0.9940070725726678, 0.9913189887798609, 0.9447943944478551, 0.9345174598215925, 0.9966714084993764,
    0.935820939526742]), width, color='b', alpha=opacity)

# axes and labels
ax.set_xlim(-width, len(ind) + width)
ax.set_ylabel('P($R$)')
xTickMarks = ['0X2000456', '0X200012E', '0X200004A', '0X200012C', '0X200012D', '0X20005A2']
ax.set_xticks(ind + width / 2)
xTickNames = ax.set_xticklabels(xTickMarks)
plt.setp(xTickNames, rotation=45, fontsize=10)
ax.legend((rects1[0], rects2[0]), ('Complete evidence', 'Single evidence'), loc='best')
plt.show()
