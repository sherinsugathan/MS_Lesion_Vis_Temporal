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
        maskFileName = rootFolder + "lesionMask\\ConsensusT1VoxelSpaceCorrected" + str(timeStep) + ".nii"
        structuralData = rootFolder + "structural\\T1_" + str(timeStep) + ".nii"
        imageMask = sitk.ReadImage(maskFileName)
        imageStructural = sitk.ReadImage(structuralData)
        connectedComponentFilter = sitk.ConnectedComponentImageFilter()
        connectedComponentImage = connectedComponentFilter.Execute(imageMask)
        
        labelStatFilter = sitk.LabelStatisticsImageFilter()
        labelStatFilter.Execute(imageStructural, connectedComponentImage)

        # load precomputed lesion properties
        structureInfo = None
        with open(jsonPath) as fp: # read source json file.
            structureInfo = json.load(fp)

        r = structureInfo[str(timeStep)]
        numberOfLesionElements = len(r[0])

        for jsonElementIndex in (range(1,numberOfLesionElements+1)):
            for p in r[0][str(jsonElementIndex)]:
                lesionDataDict = p
                lesionDataDict["Maximum"] = labelStatFilter.GetMaximum(jsonElementIndex)
                lesionDataDict["Mean"] = labelStatFilter.GetMean(jsonElementIndex)
                lesionDataDict["Median"] = labelStatFilter.GetMedian(jsonElementIndex)
                lesionDataDict["Minimum"] = labelStatFilter.GetMinimum(jsonElementIndex)
                lesionDataDict["Sigma"] = labelStatFilter.GetSigma(jsonElementIndex)
                lesionDataDict["Sum"] = labelStatFilter.GetSum(jsonElementIndex)
                lesionDataDict["Variance"] = labelStatFilter.GetVariance(jsonElementIndex)
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


