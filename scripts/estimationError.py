import numpy as np
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt

def set_shared_ylabel(figure, a, ylabel, labelpad = 0.01):
    """Set a y label shared by multiple axes
    Parameters
    ----------
    a: list of axes
    ylabel: string
    labelpad: float
        Sets the padding between ticklabels and axis label"""

    figure.canvas.draw()

    # get the center position for all plots
    top = a[0].get_position().y1
    bottom = a[-1].get_position().y0

    # get the coordinates of the left side of the tick labels
    x0 = 1
    for at in a:
        at.set_ylabel('') # just to make sure we don't and up with multiple labels
        bboxes, _ = at.yaxis.get_ticklabel_extents(figure.canvas.renderer)
        bboxes = bboxes.inverse_transformed(figure.transFigure)
        xt = bboxes.x0
        if xt < x0:
            x0 = xt
    tick_label_left = x0

    # set position of label
    a[-1].set_ylabel(ylabel)
    a[-1].yaxis.set_label_coords(tick_label_left - labelpad, (bottom + top)/2, transform=figure.transFigure)


count = []
lin = []
quad = []

count = (np.logspace(0, 1, 1000) * 100000 - 99990).astype(int)
for n in count:
    print(n)
    x = np.random.normal(10, 5, n)
    lin.append(np.sum(x * x) / (n - 1))
    quad.append((np.sum(x) ** 2) / n / (n - 1))

count = np.array(count)[5:]
lin = np.array(lin)[5:]
quad = np.array(quad)[5:]

fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True)
fig.subplots_adjust(hspace=0.02, left=0.15)

ax1.plot(count, lin, color='r')
ax1.set_ylim(121, 132)
ax2.plot(count, quad / count ** 2, color='b')
ax2.set_ylim(0, 0.0000089)

ax2.set_xlabel('Number of events')
set_shared_ylabel(fig, [ax1, ax2], 'Costs')


# create legend
redPatch = mpatches.Patch(color='red', label='Linear Costs')
bluePatch = mpatches.Patch(color='blue', label='Quadratic Costs')
ax1.legend(handles=[redPatch, bluePatch])

# draw only half of the y-axis
ax1.spines['bottom'].set_visible(False)
ax2.spines['top'].set_visible(False)
ax1.xaxis.tick_top()
ax1.tick_params(labeltop='off')
ax2.xaxis.tick_bottom()

# draw diagonals
d = 0.015
kwargs = dict(transform=ax1.transAxes, color='k', clip_on=False)
ax1.plot((-d, +d), (-d, +d), **kwargs)
ax1.plot((1 - d, 1 + d), (-d, +d), **kwargs)
kwargs.update(transform=ax2.transAxes)
ax2.plot((-d, +d), (1 - d, 1 + d), **kwargs)
ax2.plot((1 - d, 1 + d), (1 - d, 1 + d), **kwargs)

plt.show()
