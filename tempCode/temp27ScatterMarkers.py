import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import PatchCollection
from matplotlib.patches import Wedge, Circle
from math import degrees, pi

fig, ax = plt.subplots()
wedges = []
circles = []

for x in np.arange(0, 3.3, .3):
    for y in np.arange(0, 3.3, .3):
        theta, phi = np.random.random(2)  # functions of (x,y) in reality
        for v in (0, pi):
            wedges.append(Wedge((x, y),
                            .15,
                            degrees(v - phi - theta/2),
                            degrees(v - phi + theta/2),
                            edgecolor='none'),
                            )
        circles.append(Circle((x, y),
                             .15,
                             edgecolor='none'))

colors = np.linspace(0, 1, len(circles))  # function of (x,y) in reality
collection = PatchCollection(circles, cmap=plt.cm.jet, alpha=0.2)
collection.set_array(np.array(colors))
collection.set_edgecolor('none')
ax.add_collection(collection)
print(type(ax))

#wedgecolors = list(chain.from_iterable(repeat(i,2) for i in colors))
wedgecolors = np.array([colors, colors]).flatten('F') # no itertools
collection = PatchCollection(wedges, cmap=plt.cm.jet, alpha=1)
collection.set_array(np.array(wedgecolors))
collection.set_edgecolor('none')
ax.add_collection(collection)

wedges = []
circles = []

for x in np.arange(0, 3.3, .3):
    for y in np.arange(0, 3.3, .3):
        theta, phi = np.random.random(2)  # functions of (x,y) in reality
        for v in (0, pi):
            wedges.append(Wedge((x, y),
                            .15,
                            degrees(v - phi - theta/2),
                            degrees(v - phi + theta/2),
                            edgecolor='none'),
                            )
        circles.append(Circle((x, y),
                             .09,
                             edgecolor='red'))

colors = np.linspace(0, 1, len(circles))  # function of (x,y) in reality
collection = PatchCollection(circles, cmap=plt.cm.jet, alpha=0.2)
collection.set_array(np.array(colors))
collection.set_edgecolor('none')
ax.add_collection(collection)

ax.set_xlim(0,3)
ax.set_ylim(0,3)
ax.set_aspect('equal')
plt.show()