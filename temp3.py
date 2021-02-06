import numpy as np
import networkx as nx
from matplotlib import colors
import matplotlib.pyplot as plt
import matplotlib
import matplotlib.cm as cm
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


def getSplitlesionLabels(elem, data, processedList):
    labels = []
    if(elem in processedList):
        return labels
    for rowItem in data:
        if(rowItem[1] == elem):
            labels.append(rowItem[2])
    processedList.append(elem)
    return labels

nodeIndex = 0
G = nx.DiGraph()
baseLineLabels = [1,2,3,4,5]
for i in range(1, len(baseLineLabels) + 1):
    nodeIndex = i
    G.add_nodes_from([(nodeIndex, {"time":[0], "lesionLabel": [nodeIndex]})]) 

nodeIndex = nodeIndex + 1


compList = [[1,2], [3], [3], [], [5]]
t1labels = [1,2,3,4,5]

list_len = [len(i) for i in compList]
#print(list_len)


processedList = []
intersectionCountSortedList = list(sorted(zip(list_len, compList, t1labels)))
intersectionCountSortedReversedList = intersectionCountSortedList[::-1]
#print(intersectionCountSortedReversedList)

col5intersectionNodeID = 5
col2intersectionNodeID = 3
for elem in intersectionCountSortedReversedList:
    print(elem)
    if(len(elem[1]) > 1): # If intersection greater than 1
        print("merge")
        G.add_nodes_from([(nodeIndex, {"time":[0], "lesionLabel": [elem[2]]})])
        for nodeIDItem in elem[1]: 
            G.add_edge(nodeIDItem, nodeIndex)
        nodeIndex = nodeIndex + 1
    if(len(elem[1]) == 1): # If one intersection
        print("split or update")
        intersectionLabelT0 = elem[1]
        labelListT1 = getSplitlesionLabels(intersectionLabelT0, intersectionCountSortedReversedList, processedList)
        if(len(labelListT1) == 1): # intersection with a multiple intersection free label at t0. So this is just a lesion update.
            G.add_nodes_from([(elem[1][0], {"time":[0], "lesionLabel": [5]})])
        if(len(labelListT1) > 1): # intersecting with a label at t0 that has multiple intersections in t1. So this is a split scenario.
            for label in labelListT1:
                G.add_nodes_from([(nodeIndex, {"time":[0], "lesionLabel": [label]})])
                G.add_edge(col2intersectionNodeID, nodeIndex)
                nodeIndex = nodeIndex + 1
        if(len(labelListT1) == 0):
            pass
    if(len(elem[1]) == 0): # no intersection
        G.add_nodes_from([(nodeIndex, {"time":[0], "lesionLabel": [elem[2]]})])
        nodeIndex + 1

nx.draw_planar(G, with_labels=True, node_size=700, node_color="skyblue", edge_color="skyblue", node_shape="h", alpha=0.5, linewidths=2)
plt.show()

