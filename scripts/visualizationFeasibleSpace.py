import matplotlib.pyplot as plt

y1 = [0, 8]
y2 = [6, 8]

ax = plt.gca()

ax.fill_between([5, 8], [0, 8], [7.25, 8], facecolor='green', edgecolor='green', linewidth=1, interpolate=True)
ax.fill_between([0, 5], [0, 0], [6, 7.25], facecolor='green', edgecolor='green', linewidth=1, interpolate=True)
plt.plot([5, 8], y1, "k")
plt.plot([0, 8], y2, "k")
plt.scatter([0, 1, 2, 3, 4, 5,
             0, 1, 2, 3, 4, 5,
             0, 1, 2, 3, 4, 5,
             0, 1, 2, 3, 4, 5, 6,
             0, 1, 2, 3, 4, 5, 6,
             0, 1, 2, 3, 4, 5, 6,
             0, 1, 2, 3, 4, 5, 6, 7,
             4, 5, 6, 7,
             8],
            [0, 0, 0, 0, 0, 0,
             1, 1, 1, 1, 1, 1,
             2, 2, 2, 2, 2, 2,
             3, 3, 3, 3, 3, 3, 3,
             4, 4, 4, 4, 4, 4, 4,
             5, 5, 5, 5, 5, 5, 5,
             6, 6, 6, 6, 6, 6, 6, 6,
             7, 7, 7, 7,
             8])

ax.text(3.5, 7.5, 'Constraint 1',
        horizontalalignment='center',
        verticalalignment='center',
        rotation=10)

ax.text(6.75, 3.5, 'Constraint 2',
        horizontalalignment='center',
        verticalalignment='center',
        rotation=65)

plt.plot([-1, 9], [0, 0], "k")
plt.plot([0, 0], [-1, 9], "k")

plt.xlabel('x$_1$')
plt.ylabel('x$_2$')
plt.gca().set_xticks([])
plt.gca().set_yticks([])
plt.gca().spines['top'].set_visible(False)
plt.gca().spines['right'].set_visible(False)
plt.gca().spines['bottom'].set_visible(False)
plt.gca().spines['left'].set_visible(False)
plt.show()
