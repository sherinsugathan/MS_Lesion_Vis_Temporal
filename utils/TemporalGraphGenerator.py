# This function analyses all followup data and constructs a graph that represents the evolution of lesions.
import networkx as nx
import numpy as np
import os
import math
import SimpleITK as sitk
import json

from matplotlib import colors
import matplotlib.pyplot as plt
import matplotlib
import matplotlib.cm as cm
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


def getGraphData(G, nodeIndexVal, timeIndex, labelIndex):
    print(nodeIndexVal)
    print("node count ", G.number_of_nodes())
    timeSeries = G.nodes[nodeIndexVal]["time"]
    labelSeries = G.nodes[nodeIndexVal]["lesionLabel"]
    timeSeries.append(timeIndex)
    labelSeries.append(labelIndex)
    return timeSeries, labelSeries


def updateGraphNode(G, nodeID, timeIndex, label):
    nodeIDList = list(G.nodes)
    for id in nodeIDList:
        if(id == nodeID):
            timeList = G.nodes[id]["time"]
            labelList = G.nodes[id]["lesionLabel"]
            #print("LABEL LIST FROM GGGGGGGG", labelList)
            timeList.append(timeIndex)
            #print("Appended time list", timeList)
            labelList.append(label)
            G.add_nodes_from([(nodeID, {"time":timeList, "lesionLabel": labelList})])
            return
    G.add_nodes_from([(nodeID, {"time":[timeIndex], "lesionLabel": [label]})])
    print(timeIndex)
    print("NEW NODE ", nodeID, " HAS BEEN ADDED")
    return



def getNodeID(G, timeIndex, labelIndex):#, timeIndex):
    #print("tm", timeIndex)
    entered = False
    nodeIDList = list(G.nodes)
    print(nodeIDList)
    for id in nodeIDList:
        timeList = G.nodes[id]["time"] 
        #print("Stored Timelist", timeList)
        #iTimeIndex = timeList.index(int(timeIndex))
        iTimeIndex = timeList.index(timeIndex) if timeIndex in timeList else -1
        if(iTimeIndex == -1):
            continue
        #print(iTimeIndex)
        labellist = G.nodes[id]["lesionLabel"]
        #print("Stored Labellist", labellist)
        #print(iTimeIndex, labellist[iTimeIndex], labelIndex)
        if(len(labellist)!= len(timeList)):
            print("CRRRRRRRRRITICAL ERRRRRRROR")
        if(labellist[iTimeIndex] == labelIndex):
            entered = True
            return id
    if(entered == False):
        print("FALSE CASE AT", timeIndex, labelIndex)

def getSplitlesionLabels(elem, data, processedList):
    labels = []
    if(elem in processedList):
        return labels
    for rowItem in data:
        if(rowItem[1] == elem):
            labels.append(rowItem[2])
    processedList.append(elem)
    return labels

def TemporalGraphGenerator():
    G = nx.DiGraph()
    dataCount = 81
    #dataCount = 48
    graphInitialized = False
    nodeIndex = 0 
    #timeIndex = 1
    baseLineLabels = []
    rootFolder = "D:\\OneDrive - University of Bergen\\Datasets\\MS_Longitudinal\\Subject1\\"

    # Initialize graph with baseline.
    consensusFileT0 = rootFolder + "lesionMask\\Consensus"+str(0)+".nii"
    imageLesionMaskT0 = sitk.ReadImage(consensusFileT0)
    # Connected component filter T0.
    connectedComponentFilterT0 = sitk.ConnectedComponentImageFilter()
    connectedComponentImageT0 = connectedComponentFilterT0.Execute(imageLesionMaskT0)
    objectCountT0 = connectedComponentFilterT0.GetObjectCount()   

    if(graphInitialized == False):
        # Initialize graph with data from baseline.
        for j in range(1, objectCountT0 + 1):
            nodeIndex = j
            baseLineLabels.append(j)
            G.add_nodes_from([(nodeIndex, {"time":[0], "lesionLabel": [nodeIndex]})]) 
            #updateGraphNode(G, nodeIndex, 0, nodeIndex)
        graphInitialized = True
        nodeIndex = nodeIndex + 1


    for i in range(1, dataCount):
        print("MAIN ITERATION ", i, "))))))))))))))))))))))))))))))(((((((((((((((")
        consensusFileT0 = rootFolder + "lesionMask\\Consensus"+str(i-1)+".nii"
        consensusFileT1 = rootFolder + "lesionMask\\Consensus"+str(i)+".nii"
        imageLesionMaskT0 = sitk.ReadImage(consensusFileT0)
        imageLesionMaskT1 = sitk.ReadImage(consensusFileT1)
        # Connected component filter T0.
        connectedComponentFilterT0 = sitk.ConnectedComponentImageFilter()
        connectedComponentImageT0 = connectedComponentFilterT0.Execute(imageLesionMaskT0)
        objectCountT0 = connectedComponentFilterT0.GetObjectCount()   
        # Connected component filter T1.
        connectedComponentFilterT1 = sitk.ConnectedComponentImageFilter()
        connectedComponentImageT1 = connectedComponentFilterT1.Execute(imageLesionMaskT1)
        objectCountT1 = connectedComponentFilterT1.GetObjectCount()

        # if(graphInitialized == False):
        #     # Initialize graph with data from baseline.
        #     for j in range(1, objectCountT0 + 1):
        #         nodeIndex = j
        #         baseLineLabels.append(j)
        #         G.add_nodes_from([(nodeIndex, {"time":[39], "lesionLabel": [nodeIndex]})]) 
        #         #updateGraphNode(G, nodeIndex, 0, nodeIndex)
        #     graphInitialized = True
        #     nodeIndex = nodeIndex + 1
        #     continue

        processedList = []
        compList = []

        # T1 on T0
        for j in range(1, objectCountT1 + 1):
            intersectionCount = 0
            intersectionLabels = []
            # Binary threshold filter for single original lesion.
            binaryThresholdFilterSingleLesionT1 = sitk.BinaryThresholdImageFilter()
            binaryThresholdFilterSingleLesionT1.SetOutsideValue(0)
            binaryThresholdFilterSingleLesionT1.SetInsideValue(1)
            binaryThresholdFilterSingleLesionT1.SetLowerThreshold(j)
            binaryThresholdFilterSingleLesionT1.SetUpperThreshold(j)
            binaryImageSingleLesionT1 = binaryThresholdFilterSingleLesionT1.Execute(connectedComponentImageT1)
            
            for k in range(1, objectCountT0 + 1):
                # Binary threshold filter for single original lesion.
                binaryThresholdFilterSingleLesionT0 = sitk.BinaryThresholdImageFilter()
                binaryThresholdFilterSingleLesionT0.SetOutsideValue(0)
                binaryThresholdFilterSingleLesionT0.SetInsideValue(1)
                binaryThresholdFilterSingleLesionT0.SetLowerThreshold(k)
                binaryThresholdFilterSingleLesionT0.SetUpperThreshold(k)
                binaryImageSingleLesionT0 = binaryThresholdFilterSingleLesionT0.Execute(connectedComponentImageT0)
                # And filter to check intersections.
                binaryAndImageFilter = sitk.AndImageFilter()
                andedImage = binaryAndImageFilter.Execute(binaryImageSingleLesionT1, binaryImageSingleLesionT0)

                statisticsImageFilter = sitk.StatisticsImageFilter() 
                statisticsImageFilter.Execute(andedImage)
                #print(statisticsImageFilter.GetSum())
                if(statisticsImageFilter.GetSum() > 0): # intersection found, update intersection Count
                    intersectionCount = intersectionCount + 1
                    intersectionLabels.append(k)

            #     print(j, k, int(statisticsImageFilter.GetSum()), intersectionCount)
            # print("=====================================")

            compList.append(intersectionLabels)
        t1labels = list(range(1,objectCountT1+1))
        list_len = [len(i) for i in compList]
        print("COMPLIST", compList)

        processedList = []
        intersectionCountSortedList = list(sorted(zip(list_len, compList, t1labels)))
        intersectionCountSortedReversedList = intersectionCountSortedList[::-1]
        #print(intersectionCountSortedReversedList)
 
        for elem in intersectionCountSortedReversedList:
            #print(elem)
            if(len(elem[1]) > 1): # If intersection greater than 1
                print("merge")
                #G.add_nodes_from([(nodeIndex, {"time":[i+1], "lesionLabel": [elem[2]]})])
                updateGraphNode(G, nodeIndex, i, elem[2])
                for labelValue in elem[1]: 
                    nodeID = getNodeID(G, i-1, labelValue)
                    G.add_edge(nodeID, nodeIndex)
                nodeIndex = nodeIndex + 1

            if(len(elem[1]) == 1): # If one intersection
                #print("split or update")
                intersectionLabelT0 = elem[1]
                labelListT1 = getSplitlesionLabels(intersectionLabelT0, intersectionCountSortedReversedList, processedList)
                if(len(labelListT1) == 1): # intersection with a multiple intersection free label at t0. So this is just a lesion update.+
                    print("mark entry 1")
                    #print("ekem 1 0 ", elem[1][0])
                    nodeID = getNodeID(G, i-1, elem[1][0])
                    #print("i val is ", i, nodeID)
                    #G.add_nodes_from([(nodeID, {"time":[i+1], "lesionLabel": [elem[2]]})])
                    updateGraphNode(G, nodeID, i, elem[2])
                
                if(len(labelListT1) > 1): # intersecting with a label at t0 that has multiple intersections in t1. So this is a split scenario.
                    nodeID = getNodeID(G, i-1, elem[1][0])
                    print("mark entry 2a")
                    for label in labelListT1:
                        print("mark entry 2b")
                        #G.add_nodes_from([(nodeIndex, {"time":[i+1], "lesionLabel": [label]})])
                        print(nodeIndex)
                        updateGraphNode(G, nodeIndex, i, label)
                        G.add_edge(nodeID, nodeIndex)
                        nodeIndex = nodeIndex + 1
                
                if(len(labelListT1) == 0):
                    print("mark entry 3")
                    pass

            if(len(elem[1]) == 0): # no intersection
                #G.add_nodes_from([(nodeIndex, {"time":[i+1], "lesionLabel": [elem[2]]})])
                updateGraphNode(G, nodeIndex, i, elem[2])
                print("newwwwww lewsion")
                nodeIndex = nodeIndex + 1




            # if(intersectionCount == 0):
            #     print("new lesion")
            # if(intersectionCount == 1):
            #     print("lesion update")
            # if(intersectionCount > 1):
            #     print("merge")
            # if(intersectionCount == 1):
            #     print("do nothing")
            #     pass
            # if(intersectionCount > 1):
            #     print("lesion merge")
            #     for intersectionIndex in intersectionIndices:
            #         G.add_nodes_from([(nodeIndex, {"time":[i], "lesionLabel": [j]})]) 
            #         mergeComponentIndex = getNodeIndex(G, intersectionIndex)
            #         G.add_edge(mergeComponentIndex, nodeIndex)
            #         nodeIndex = nodeIndex + 1
            #         #G.add_nodes_from([(nodeIndex, {"time":[0], "lesionLabel": [j]})]) 
                
            # if(intersectionCount == 0):
            #     print("lesion appear")
            #     print("NEW NODE INDEX", nodeIndex)
            #     G.add_nodes_from([(nodeIndex, {"time":[i], "lesionLabel": [j]})]) 
            #     nodeIndex = nodeIndex + 1

   

        #timeIndex = timeIndex + 1
    # print("NODE 8 TIMELIST", G.nodes[8]["time"])
    # print("NODE 8 LABELS", G.nodes[8]["lesionLabel"])

    # print("NODE 9 TIMELIST", G.nodes[9]["time"])
    # print("NODE 9 LABELS", G.nodes[9]["lesionLabel"])
    nx.write_gml(G, "D:\\geeksforgeeks.gml") # save graph
    nx.draw(G, with_labels=True, node_size=1500, node_color="skyblue", node_shape="h", alpha=0.5, linewidths=3)
    plt.show()



    #nx.draw(G, with_labels=True, node_size=1500, node_color="skyblue", node_shape="s", alpha=0.5, linewidths=40)
    #plt.show()

TemporalGraphGenerator()