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



c = np.full(6,255, dtype='B')
c =c.astype('B').reshape((2,3))
print(c)







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