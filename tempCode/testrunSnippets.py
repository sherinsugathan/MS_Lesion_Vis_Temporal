import seaborn as sns
import numpy as np
from matplotlib import colors
import matplotlib.pyplot as plt
import matplotlib
import matplotlib.cm as cm
import networkx as nx
import json
from scipy.ndimage.filters import gaussian_filter1d


G = nx.read_gml("D:\\OneDrive - University of Bergen\\Datasets\\MS_Longitudinal\\Subject1\\preProcess\\lesionGraph.gml")
connectedComponents = nx.strongly_connected_components(G)
UG = G.to_undirected()
sub_graphs = list(nx.connected_components(UG))

for item in sub_graphs:
    print((list(item)))

for item in sub_graphs:
    print((list(item)))