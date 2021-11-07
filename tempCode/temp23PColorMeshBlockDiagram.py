import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LogNorm
import matplotlib.ticker as ticker

dataCount=10
Z = np.random.rand(2, dataCount)
plt.imshow(Z)

ax = plt.gca()
fig = plt.gcf()

fig.set_figheight(2)
ax.set_yticks([0, 1])  # Set two values as ticks.
print(ax.get_xticks().tolist())
ax.set_xticks(list(range(dataCount)))  # Set two values as ticks.
modalities = ["T1", "T2"]
ax.set_yticklabels(modalities)


ax.tick_params(axis='x', which='minor', length=1)

plt.title("Lesion Intensity")
plt.show()