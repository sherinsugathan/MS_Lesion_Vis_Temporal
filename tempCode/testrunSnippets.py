import seaborn as sns
import numpy as np
from matplotlib import colors
import matplotlib.pyplot as plt
import matplotlib
import matplotlib.cm as cm
import networkx as nx
import json
import vtk
from scipy.ndimage.filters import gaussian_filter1d

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




def hinton(matrix, max_weight=None, ax=None):
    """Draw Hinton diagram for visualizing a weight matrix."""
    ax = ax if ax is not None else plt.gca()
    #if not max_weight:
    #    max_weight = 2 ** np.ceil(np.log(np.abs(matrix).max()) / np.log(2))

    max_weight = 0.5

    ax.patch.set_facecolor('gray') # Background color
    ax.set_aspect('equal', 'box')
    #ax.xaxis.set_major_locator(plt.NullLocator())
    #ax.yaxis.set_major_locator(plt.NullLocator())

    for (x, y), w in np.ndenumerate(matrix):
        color = 'white' if w > 0 else 'black'
        size = np.sqrt(np.abs(w) / max_weight)
        print(size)
        rect = plt.Rectangle([x - size / 2, y - size / 2], size, size,
                             facecolor=color, edgecolor=color)
        ax.add_patch(rect)

    ax.autoscale_view()
    ax.invert_yaxis()

if __name__ == '__main__':
    # Fixing random state for reproducibility
    np.random.seed(19680801)
    hinton(np.random.rand(80, 20) -0.5)
    plt.show()


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