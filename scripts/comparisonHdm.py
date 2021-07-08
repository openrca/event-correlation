#!/usr/bin/env python
import matplotlib.pyplot as plt
import numpy as np

opacity = 0.9

# Single trigger
ind = np.arange(6)
width = 0.75
fig = plt.figure()
ax = fig.add_subplot(111)
# bars1 = ax.bar(ind, 1 - np.array([
#     0.9977980690759589, 0.9988978210770524, 0.9988978210770523, 0.9977980690759589, 0.99970217206124,
#     0.9946879366150463]), width, color='r', alpha=opacity)
bars2 = ax.bar(ind, 1 - np.array([
    0.9447943944478551, 0.9345174598215925, 0.9966714084993764, 0.9913189887798609, 0.9940070725726678,
    0.935820939526742]), width, color='b', alpha=opacity)
ax.set_ylabel('P($R$ | $\mathcal{E}$ )')
ax.set_xlim(-width, len(ind) + width)
ax.set_xlabel('Evidence $\mathcal{E}$')
ax.set_xticks(ind + width / 2)
ax.set_xticklabels(['0X04A', '0X12C', '0X12D', '0X12E', '0X456', '0X5A2'])
# ax.legend((bars1[0], bars2[0]), ('Complete evidence', 'Single evidence'), loc='best')
plt.tight_layout()
fig.savefig('hdm_one.pdf', format='PDF', transparent=True)

# Multiple Triggers
ind = np.arange(4)
width = 0.75
fig = plt.figure()
ax = fig.add_subplot(111)
ax.bar(ind, np.array([0.016918777286092715, 0.06978722448837131, 0.8539272714426238, 0.8917679732785454]),
       width, alpha=opacity)
ax.set_ylim(0, 1)
ax.set_ylabel('P($R$ | $\mathcal{E}$ )')
ax.set_xlabel('Evidence $\mathcal{E}$')
ax.set_xlim(-width / 2, len(ind) + width / 2)
ax.set_xticks(ind + width / 2)
ax.set_xticklabels(['0X456,\n0X12D', '0X456,\n0X12E', '0X5A2,\n0X04A', '0X12C,\n0X5A2'])

plt.tight_layout()
plt.show()
fig.savefig('hdm_two.pdf', format='PDF', transparent=True)