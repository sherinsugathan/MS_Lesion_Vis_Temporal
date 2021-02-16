import numpy as np
from matplotlib import colors
import matplotlib.pyplot as plt
import matplotlib
import matplotlib.cm as cm
import networkx as nx
import json
from scipy.ndimage.filters import gaussian_filter1d

# Fixing random state for reproducibility
np.random.seed(19680801)
G = nx.read_gml("D:\\OneDrive - University of Bergen\\Datasets\\MS_Longitudinal\\Subject1\\preProcess\\lesionGraph.gml")


def getDataFromJson(time, label, key):
    # load precomputed lesion properties
    with open("D:\\OneDrive - University of Bergen\\Datasets\\MS_Longitudinal\\Subject1" + "\\preProcess\\lesionStatistics.json") as fp: 
        structureInfo = json.load(fp)
    numberOfFollowups = len(structureInfo)
    #print("NUMBER OF DATA POINTS IN JSON", numberOfFollowups)
    return structureInfo[str(time)][0][str(label)][0][key]


#x = np.linspace(0, 81, 82)
x = list(range(81))
#x = np.linspace(0, 5, 5)
# for _ in range(3):
#     print(gaussian_mixture(x))
#     print("////////////////////////////////////")

# buckets = [0] * 5
# print(buckets)
nodeIDList = list(G.nodes)
#ss = list(G.degree(nodeIDList))

#ss = list(G.neighbors('2'))

nodesAndDegreesUndirected =  list(G.degree(nodeIDList))
nodesAndDegreesDirectedOut =  list(G.out_degree(nodeIDList))
nodesAndDegreesDirectedIn =  list(G.in_degree(nodeIDList))
disconnectedNodes = [elem[0] for elem in nodesAndDegreesUndirected if elem[1]==0]
splitNodes = [elem[0] for elem in nodesAndDegreesDirectedOut if elem[1]>1]
mergeNodes = [elem[0] for elem in nodesAndDegreesDirectedIn if elem[1]>1]
nodeOrderForGraph = disconnectedNodes
for elem in mergeNodes:
    nodeOrderForGraph.append(elem)
    for i in [item for item in nx.ancestors(G, elem)]:
        nodeOrderForGraph.append(i)
for elem in splitNodes:
    nodeOrderForGraph.append(elem)
    for i in [item[0] for item in G[elem]]:
        nodeOrderForGraph.append(i)

print(nodeOrderForGraph)
#quit()

ys = []
dataArray = []
print(nodeIDList)
for id in nodeOrderForGraph:
    timeList = G.nodes[id]["time"]
    #print("TIMELIST LENGTH", len(timeList))
    # print(timeList)
    # print(timeList[0],timeList[-1])
    # quit()
    #print(len(timeList))

    labelList = G.nodes[id]["lesionLabel"]
    data = []
    for i in range(len(timeList)):
        time = timeList[i]
        label = labelList[i]
        dataItem = getDataFromJson(time, label, "NumberOfPixels")
        data.append(dataItem)
    buckets = [0] * 81
    
    buckets[timeList[0]:timeList[-1]+1] = data
    buckets = gaussian_filter1d(buckets, sigma=2)
    arr = np.asarray(buckets, dtype=np.float64)
    print("BUCKET LENGTH", len(buckets))
    dataArray.append(arr)

#print(dataArray)
#print(len(dataArray))
    

#ys = [gaussian_mixture(x) for _ in range(3)]
#print(ys)

#m = dataArray[0]
#print(m.dtype)
ys = dataArray


fig, ax = plt.subplots()
ax.stackplot(x, ys, baseline='wiggle')
plt.show()