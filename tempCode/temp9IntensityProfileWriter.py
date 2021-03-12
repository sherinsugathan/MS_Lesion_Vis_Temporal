
# read structural data and write synthetic intensity profiles.
from datetime import time
from typing import final
import SimpleITK as sitk
import vtk
import numpy as np
import sys, os
import math
import ctypes
import csv
from itertools import cycle
import networkx as nx

rootPath = "D:\\OneDrive - University of Bergen\\Datasets\\MS_Longitudinal\\Subject1\\"
fileNameT1 = rootPath + "\\structural\\T1.nii"
#fileNameMaskLabels = rootPath + "\\lesionMask\\ConnectedComponents.nii"
G = nx.read_gml("D:\\OneDrive - University of Bergen\\Datasets\\MS_Longitudinal\\Subject1\\preProcess\\lesionGraph.gml")
UG = G.to_undirected()
sub_graphs = list(nx.connected_components(UG))

dataCount = 81

# Get nodeID for a label and timestep.
def getNodeIDfromLabelAndTimeStep(label, timeStep):
    nodeIDList = list(G.nodes)
    for id in nodeIDList:
        timeList = G.nodes[id]["time"]
        labelList = G.nodes[id]["lesionLabel"]
        temporalData = list(zip(timeList, labelList))
        if((timeStep, label) in list(temporalData)):
            return id
    return None

# Get label for node at specific time of any timestep provided the current ID and timestep.
def getLabelForNodeIDTimeStep(G, nodeId, queryTimeStep):
    nodeIDList = list(G.nodes)
    timeList = G.nodes[str(nodeId)]["time"]
    labelList = G.nodes[str(nodeId)]["lesionLabel"]
    #print(timeList)
    #print(labelList)
    #print(labelList[timeList.index(queryTimeStep)])
    return labelList[timeList.index(queryTimeStep)]

def getIntensityValue(label, timeStep):
    #print("label", label, "timeStep", timeStep)
    nodeID = getNodeIDfromLabelAndTimeStep(label, timeStep)
    #print("node id", nodeID)
    #search node_id in sub_graphs and get the index
    dataIndex = [sub_graphs.index(elem) for elem in sub_graphs if str(nodeID) in list(elem)]
    #print("dataIndex", dataIndex)
    # get the array from proper index and return timeStep item.
    intensityArray = subgraph_IntensityList[dataIndex[0]]
    return intensityArray[timeStep]

def updateStructuralData(imageT1, timeStep):
    imageConsensus = sitk.ReadImage(rootPath + "\\lesionMask\\ConsensusT1VoxelSpaceCorrected"+ str(timeStep) +".nii")
    connectedComponentFilter = sitk.ConnectedComponentImageFilter()
    connectedComponentImage = connectedComponentFilter.Execute(imageConsensus)
    #objectCount = connectedComponentFilter.GetObjectCount()

    for i in range(dimensions[0]):
        for j in range(dimensions[1]):
            for k in range(dimensions[2]):
                voxelLabel = connectedComponentImage.GetPixel(i, j, k)
                if(voxelLabel != 0):
                    intensityValue = getIntensityValue(voxelLabel, timeStep)
                    newVoxel = imageT1.GetPixel(i,j,k) + intensityValue
                    if(newVoxel<0):
                        newVoxel = 0
                    imageT1[i,j,k] = newVoxel


intensityProfile = {"hyper":150, "hyper2":100, "iso":0, "hypo":-400, "hypo2": -200}
#0: HYPER
#1: ISO 
#2: HYPO 


prof1= ["hypo", "iso", "hyper", "hyper2"]
prof2= ["hypo", "iso", "hyper"]
prof3= ["iso", "iso"]
prof4= ["hypo", "hypo2"]
prof5= ["hyper", "hyper2"]
profilePool = []
profilePool.append(prof1)
profilePool.append(prof2)
profilePool.append(prof3)
profilePool.append(prof4)
profilePool.append(prof5)
pool = cycle(profilePool)


intVector = [0]*dataCount
splitPercentage = 100/(len(prof1)-1)
sectionSize = math.floor(splitPercentage*len(intVector)/100)

subgraph_IntensityList = []
for elem in sub_graphs:
    finalList = []
    profile = next(pool)
    print(profile)
    for i in range(len(profile)-1):
        finalList = finalList + list(np.linspace(intensityProfile[profile[i]], intensityProfile[profile[i+1]], sectionSize, endpoint=True))
    subgraph_IntensityList.append(finalList)

countDiff = dataCount - len(finalList)

if(countDiff>0):
    finalList = finalList + [finalList[-1]]*countDiff

#print(finalList)
#print(len(finalList))
#quit()

# read and get voxel array from MRI data.

#imageConnectedComponents = sitk.ReadImage(fileNameMaskLabels)



#labelShapeStatisticsFilter = sitk.LabelShapeStatisticsImageFilter()
#labelShapeStatisticsFilter.Execute(imageConnectedComponents)
#labelCount = labelShapeStatisticsFilter.GetNumberOfLabels()

#print("Number of lesion labels", labelCount)
#print("Labels:", labelShapeStatisticsFilter.GetLabels())
#print("Structural data pixel type", imageT1.GetPixelIDTypeAsString())


#updateStructuralData(imageT1, 150)

for timeStep in range(1):
    imageT1 = sitk.ReadImage(fileNameT1)
    dimensions = imageT1.GetSize()
    updateStructuralData(imageT1, timeStep)
    print("Processed Volume", timeStep)
    sitk.WriteImage(imageT1, "D:\\T1_"+str(timeStep)+".nii")

print("File write complete")
