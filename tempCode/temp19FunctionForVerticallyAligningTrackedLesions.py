from networkx.algorithms.components.connected import connected_components
import networkx as nx
from networkx.generators.classic import star_graph
import numpy as np
from iteration_utilities import deepflatten

# read graph.
G = nx.read_gml("D:\\OneDrive - University of Bergen\\Datasets\\MS_Longitudinal\\Subject1\\preProcess\\lesionGraph.gml")
#connectedComponents = nx.connected_components(G.to_undirected())
connectedComponents = nx.weakly_connected_components(G)
# Compute order.se nodes
orderedNodes = []
print(G.edges)
quit()

for item in connectedComponents:
    g = G.subgraph(item)
    levelWiseNodes = []
    nodeLabels = []
    rootNodes = [n for n,d in g.in_degree() if d==0]
    nodeDict = nx.single_source_shortest_path_length(g,rootNodes[0])
    uniqueValues = list(set(nodeDict.values()))
    #print(uniqueValues)
    levelWiseNodes.append(rootNodes)
    maxNodeCount  = len(rootNodes)

    # if ((maxNodeCount % 2) == 0): # even identified
    #     print("even identified")
    # else: # odd identified.
    #     pass
    
    for i in range(1,len(uniqueValues)):
        levelNodes = [k for k,v in nodeDict.items() if v == uniqueValues[i]]
        #print("LEVEL NODES", levelNodes)
        levelNodeCount = len(levelNodes)
        # if ((levelNodeCount % 2) == 0):
        #     print("even identified")
        if(levelNodeCount > maxNodeCount):
            maxNodeCount = len(levelNodes)
        levelWiseNodes.append(levelNodes)
    #print("MAX IS", maxNodeCount)
    #print([n for n,d in g.in_degree() if d==0])
    #print(list(nx.bfs_edges(g, rootNodes[0])))
    #print(nx.single_source_mshortest_path_length(g,rootNodes[0]))
    #print("LEVELWISENODES", levelWiseNodes)
    orderedNodes.append(levelWiseNodes)
print("DONE")
print(orderedNodes)

for elem in orderedNodes:
    print(elem)
    print("LENGTH", len(elem))
    print("MAX is", max([len(a) for a in elem]))
    print("=============================")