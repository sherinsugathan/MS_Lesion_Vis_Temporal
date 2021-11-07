import matplotlib.collections as mcollections

import matplotlib.pyplot as plt
import matplotlib as mpl


class UpdatablePatchCollection(mcollections.PatchCollection):
    def __init__(self, patches, *args, **kwargs):
        self.patches = patches
        mcollections.PatchCollection.__init__(self, patches, *args, **kwargs)

    def get_paths(self):
        self.set_paths(self.patches)
        return self._paths


rect = mpl.patches.Rectangle((0,0),1,1)

rect.set_xy((1,1))
collection = UpdatablePatchCollection([rect])
rect.set_xy((2,2))

ax = plt.figure(None).gca()
ax.set_xlim(0,5)
ax.set_ylim(0,5)
ax.add_artist(collection)
plt.show()  # now shows a rectangle at (2,2)