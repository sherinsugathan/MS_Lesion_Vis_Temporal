from matplotlib import pyplot as plt
import numpy as np

fig, axes = plt.subplots(nrows=1, ncols = 2)
ax1,ax2 = axes
fig_width = fig.get_figwidth()
fig_height = fig.get_figheight()
fig_factor = 1.0

##saving some values
xlim = dict()
ylim = dict()
lines = dict()
line_sizes = dict()
paths = dict()
point_sizes = dict()

## a line plot
x1 = np.linspace(0,np.pi,30)
y1 = np.sin(x1)

lines[ax1] = ax1.plot(x1, y1, 'ro', markersize = 3, alpha = 0.8)
xlim[ax1] = ax1.get_xlim()
ylim[ax1] = ax1.get_ylim()
line_sizes[ax1] = [line.get_markersize() for line in lines[ax1]]


## a scatter plot
x2 = np.random.normal(1,1,30)
y2 = np.random.normal(1,1,30)

paths[ax2] = ax2.scatter(x2,y2, c = 'b', s = 20, alpha = 0.6)
point_sizes[ax2] = paths[ax2].get_sizes()

xlim[ax2] = ax2.get_xlim()
ylim[ax2] = ax2.get_ylim()


def on_resize(event):
    global fig_factor

    w = fig.get_figwidth()
    h = fig.get_figheight()

    fig_factor = min(w/fig_width,h/fig_height)

    for ax in axes:
        lim_change(ax)


def lim_change(ax):
    lx = ax.get_xlim()
    ly = ax.get_ylim()

    factor = min(
        (xlim[ax][1]-xlim[ax][0])/(lx[1]-lx[0]),
        (ylim[ax][1]-ylim[ax][0])/(ly[1]-ly[0])
    )

    try:
        for line,size in zip(lines[ax],line_sizes[ax]):
            line.set_markersize(size*factor*fig_factor)
    except KeyError:
        pass


    try:
        paths[ax].set_sizes([s*factor*fig_factor for s in point_sizes[ax]])
    except KeyError:
        pass

fig.canvas.mpl_connect('resize_event', on_resize)
for ax in axes:
    ax.callbacks.connect('xlim_changed', lim_change)
    ax.callbacks.connect('ylim_changed', lim_change)
plt.show()










# import seaborn as sns
# #import numpy as np
# from matplotlib import colors
# import matplotlib.pyplot as plt
# import matplotlib
# import matplotlib.cm as cm
# import networkx as nx
# import json
# import vtk
# from scipy.ndimage.filters import gaussian_filter1d
# from matplotlib.pyplot import figure, show
# import numpy

# class ZoomPan:
#     def __init__(self):
#         self.press = None
#         self.cur_xlim = None
#         self.cur_ylim = None
#         self.x0 = None
#         self.y0 = None
#         self.x1 = None
#         self.y1 = None
#         self.xpress = None
#         self.ypress = None


#     def zoom_factory(self, ax, base_scale = 2.):
#         def zoom(event):
#             cur_xlim = ax.get_xlim()
#             cur_ylim = ax.get_ylim()

#             xdata = event.xdata # get event x location
#             ydata = event.ydata # get event y location

#             if event.button == 'down':
#                 # deal with zoom in
#                 scale_factor = 1 / base_scale
#             elif event.button == 'up':
#                 # deal with zoom out
#                 scale_factor = base_scale
#             else:
#                 # deal with something that should never happen
#                 scale_factor = 1
#                 print(event.button)

#             new_width = (cur_xlim[1] - cur_xlim[0]) * scale_factor
#             new_height = (cur_ylim[1] - cur_ylim[0]) * scale_factor

#             relx = (cur_xlim[1] - xdata)/(cur_xlim[1] - cur_xlim[0])
#             rely = (cur_ylim[1] - ydata)/(cur_ylim[1] - cur_ylim[0])

#             ax.set_xlim([xdata - new_width * (1-relx), xdata + new_width * (relx)])
#             ax.set_ylim([ydata - new_height * (1-rely), ydata + new_height * (rely)])
#             ax.figure.canvas.draw()

#         fig = ax.get_figure() # get the figure of interest
#         fig.canvas.mpl_connect('scroll_event', zoom)

#         return zoom

#     def pan_factory(self, ax):
#         def onPress(event):
#             if event.inaxes != ax: return
#             self.cur_xlim = ax.get_xlim()
#             self.cur_ylim = ax.get_ylim()
#             self.press = self.x0, self.y0, event.xdata, event.ydata
#             self.x0, self.y0, self.xpress, self.ypress = self.press

#         def onRelease(event):
#             self.press = None
#             ax.figure.canvas.draw()

#         def onMotion(event):
#             if self.press is None: return
#             if event.inaxes != ax: return
#             dx = event.xdata - self.xpress
#             dy = event.ydata - self.ypress
#             self.cur_xlim -= dx
#             self.cur_ylim -= dy
#             ax.set_xlim(self.cur_xlim)
#             ax.set_ylim(self.cur_ylim)

#             ax.figure.canvas.draw()

#         fig = ax.get_figure() # get the figure of interest

#         # attach the call back
#         fig.canvas.mpl_connect('button_press_event',onPress)
#         fig.canvas.mpl_connect('button_release_event',onRelease)
#         fig.canvas.mpl_connect('motion_notify_event',onMotion)

#         #return the function
#         return onMotion

# fig = figure()

# ax = fig.add_subplot(111, xlim=(0,1), ylim=(0,1), autoscale_on=False)

# ax.set_title('Click to zoom')
# x,y,s,c = numpy.random.rand(4,200)
# s *= 200

# ax.scatter(x,y,s,c)
# scale = 1.1
# zp = ZoomPan()
# figZoom = zp.zoom_factory(ax, base_scale = scale)
# figPan = zp.pan_factory(ax)
# show()









# G = nx.read_gml("D:\\OneDrive - University of Bergen\\Datasets\\MS_Longitudinal\\Subject1\\preProcess\\lesionGraph.gml")
# connectedComponents = nx.strongly_connected_components(G)
# UG = G.to_undirected()
# sub_graphs = list(nx.connected_components(UG))

# for item in sub_graphs:
#     print((list(item)))

# H = G.subgraph(['8', '9', '2'])
# print(list(H.edges))

# leaf_nodes = [x for x in H.nodes() if H.out_degree(x)==0 and H.in_degree(x)==1]
# print(len(leaf_nodes))
# print("done")




# def hinton(matrix, max_weight=None, ax=None):
#     """Draw Hinton diagram for visualizing a weight matrix."""
#     ax = ax if ax is not None else plt.gca()
#     #if not max_weight:
#     #    max_weight = 2 ** np.ceil(np.log(np.abs(matrix).max()) / np.log(2))

#     max_weight = 0.5

#     ax.patch.set_facecolor('gray') # Background color
#     ax.set_aspect('equal', 'box')
#     #ax.xaxis.set_major_locator(plt.NullLocator())
#     #ax.yaxis.set_major_locator(plt.NullLocator())

#     for (x, y), w in np.ndenumerate(matrix):
#         color = 'white' if w > 0 else 'black'
#         size = np.sqrt(np.abs(w) / max_weight)
#         print(size)
#         rect = plt.Rectangle([x - size / 2, y - size / 2], size, size,
#                              facecolor=color, edgecolor=color)
#         ax.add_patch(rect)

#     ax.autoscale_view()
#     ax.invert_yaxis()

# if __name__ == '__main__':
#     # Fixing random state for reproducibility
#     np.random.seed(19680801)
#     hinton(np.random.rand(80, 20) -0.5)
#     plt.show()


#c = np.full(6,255, dtype='B')
#c =c.astype('B').reshape((2,3))
#print(c)







# numberOfPointsLh = 2
# vtk_colorsLh = vtk.vtkUnsignedCharArray()
# #vtk_colorsLh = vtk.vtkFloatArray()
# vtk_colorsLh.SetNumberOfComponents(3)
# vtk_colorsLh.SetNumberOfTuples(2)
# c = np.full(numberOfPointsLh, 0, dtype='B')
# #c = np.array([1,2,3,4,5], 'f')
# print(c)

# vtk_colorsLh.SetArray( c, c.size, True)





# G = nx.read_gml("D:\\OneDrive - University of Bergen\\Datasets\\MS_Longitudinal\\Subject1\\preProcess\\lesionGraph.gml")
# connectedComponents = nx.strongly_connected_components(G)
# UG = G.to_undirected()
# sub_graphs = list(nx.connected_components(UG))

# for item in sub_graphs:
#     print((list(item)))

# for item in sub_graphs:
#     print((list(item)))