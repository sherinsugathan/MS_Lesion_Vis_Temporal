from networkx.algorithms.components.connected import connected_components
import networkx as nx
from networkx.generators.classic import star_graph
import numpy as np
from iteration_utilities import deepflatten

def insertChildren(sourceList, dataList, targetNode):
    targetIndex = sourceList.index(targetNode) + 1
    # Find middle of data List
    length = len(dataList)
    middle_index = length//2
    first_half = dataList[:middle_index]
    second_half = dataList[middle_index:]
    sourceList.insert(targetIndex-1, first_half)
    sourceList.insert(targetIndex+1, second_half)
    flatten_list = list(deepflatten(sourceList))
    return flatten_list


#sourceList = [1,2,3,4,5,6,7,8,9]    
#dataList = [11,12,13,14]
#targetNode = 1
#print(insertChildren(sourceList, dataList, targetNode))
#quit()

# read graph.
G = nx.read_gml("D:\\OneDrive - University of Bergen\\Datasets\\MS_Longitudinal\\Subject1\\preProcess\\lesionGraph.gml")
#connectedComponents = nx.connected_components(G.to_undirected())
connectedComponents = nx.weakly_connected_components(G)
# Compute order.
finalList = []
for item in connectedComponents:
    g = G.subgraph(item)
    if(len(g.edges) == 0): # Single node.
        pass
    else: # split or merge event
        stack = []
        processedRootChildren = []
        print("TOP SORT", list(nx.topological_sort(g)))
        print("EDGES", g.edges)
        print("ROOT", [n for n,d in g.in_degree() if d==0] )
        rootNodes = [n for n,d in g.in_degree() if d==0]    

        if(len(rootNodes)>1): # Multiple start points for tracking
            for root in rootNodes:
                print(root)
                rootChildren = list(g.successors(root))
                if(rootChildren not in processedRootChildren):
                    processedRootChildren.append(rootChildren)
        else: # Single start point for tracking
            finalList.append(rootNodes[0])
            rootChildren = list(g.successors(rootNodes[0]))
            stack.extend(rootChildren)
            print("Hi", insertChildren(finalList, stack, rootNodes[0]))
            poppedItem = stack.pop()
            while(poppedItem):
                print(type(poppedItem))
                it = list(g.successors(poppedItem))
                #print("dfd", poppedItem, it)
                if(len(stack)!=0): # TO BE TESTED BEFORE USE. (Current data does not enter this scenario)
                    poppedItem = stack.pop()
                else:
                    break

            #quit()
            #stack.append(rootChildren)


        #print(list(item)[0])
    print("nodes", item)
    
    #print(len(g.edges))
# display order.
print("done")