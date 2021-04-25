# Using lesion mask and structural data, write intensity statistics(mean, median, variance, std etc.) to json file.
import vtk
import numpy as np
import os
import math
import SimpleITK as sitk
import json

def IntensityStatisticsJSONWriter():
    rootFolder = "C:\\Sherin\\OneDrive - University of Bergen\\Datasets\\MS_Longitudinal\\Subject1\\"
    jsonPath = rootFolder + "preProcess\\lesionStatistics.json"
    dataCount = 81
    dataDictMain = {}
    for timeStep in range(dataCount):
        data = {}
        print("Processing timestep:", timeStep)
        maskFileName = rootFolder + "lesionMask\\ConsensusT2VoxelSpaceCorrected" + str(timeStep) + ".nii"
        #maskFileName = rootFolder + "lesionMask\\Consensus" + str(timeStep) + ".nii"
        structuralData = rootFolder + "structural\\T2_" + str(timeStep) + ".nii"
        imageMask = sitk.ReadImage(maskFileName)
        imageStructural = sitk.ReadImage(structuralData)
        connectedComponentFilter = sitk.ConnectedComponentImageFilter()
        connectedComponentImage = connectedComponentFilter.Execute(imageMask)
        #sitk.WriteImage(connectedComponentImage, "D:\\connectedTest.nii")
        objectCount = connectedComponentFilter.GetObjectCount()
        
        
        labelStatFilter = sitk.LabelStatisticsImageFilter()
        labelStatFilter.Execute(imageStructural, connectedComponentImage)
        #print("object count", objectCount)
        #print("number of connected components", labelStatFilter.GetLabels())

        # load precomputed lesion properties
        structureInfo = None
        with open(jsonPath) as fp: # read source json file.
            structureInfo = json.load(fp)

        r = structureInfo[str(timeStep)]
        numberOfLesionElements = len(r[0])
        #print("number of lesion elements", numberOfLesionElements)
        #print("number of lesion labels", labelStatFilter.GetNumberOfLabels())

        for jsonElementIndex in (range(1,numberOfLesionElements+1)):
            for p in r[0][str(jsonElementIndex)]:
                lesionDataDict = p
                lesionDataDict["MaximumT2"] = labelStatFilter.GetMaximum(jsonElementIndex)
                lesionDataDict["MeanT2"] = labelStatFilter.GetMean(jsonElementIndex)
                lesionDataDict["MedianT2"] = labelStatFilter.GetMedian(jsonElementIndex)
                lesionDataDict["MinimumT2"] = labelStatFilter.GetMinimum(jsonElementIndex)
                lesionDataDict["SigmaT2"] = labelStatFilter.GetSigma(jsonElementIndex)
                lesionDataDict["SumT2"] = labelStatFilter.GetSum(jsonElementIndex)
                #print(lesionDataDict["Sum"])
                lesionDataDict["VarianceT2"] = labelStatFilter.GetVariance(jsonElementIndex)
                data[jsonElementIndex]=[]
                data[jsonElementIndex].append(lesionDataDict)

        dataDictMain[timeStep] = []
        dataDictMain[timeStep].append(data)
    
    with open(jsonPath, 'w') as fp:
        json.dump(dataDictMain, fp, indent=4)


'''
##########################################################################
    MAIN SCRIPT
    Returns: Success :)
##########################################################################
'''
IntensityStatisticsJSONWriter()
print("Processing completed successfully")


