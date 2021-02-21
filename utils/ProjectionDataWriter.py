# Write a JSON file that stores parcellation information.
import SimpleITK as sitk
import vtk
import numpy as np
import json
import sys
from nibabel import freesurfer
import operator

'''
##########################################################################
    Compute surface mapping and write to json file
    Returns: none.
##########################################################################
'''
def ComputeAndWriteParcellationData(dataCount, dataType):
    dataDictMainLh = {}
    dataDictMainRh = {}
    structureInfo = None
    with open(rootPath + "preProcess\\lesionStatistics.json") as fp: 
        structureInfo = json.load(fp)
    #numberOfLesionElements = len(structureInfo)
    # Process all time step.
    for timeIndex in range(dataCount):
        subjectFolder = rootPath
        # Files
        if(dataType == "STRUCTURAL"):
            parcellationJSONFileNameLh = subjectFolder + "\\preProcess\\" + "parcellationLh.json"
            parcellationJSONFileNameRh = subjectFolder + "\\preProcess\\" + "parcellationRh.json"
        if(dataType == "DTI"):
            parcellationJSONFileNameLh = subjectFolder + "\\preProcess\\" + "parcellationLhDTI.json"
            parcellationJSONFileNameRh = subjectFolder + "\\preProcess\\" + "parcellationRhDTI.json"
        if(dataType == "DANIELSSON"):
            parcellationJSONFileNameLh = subjectFolder + "\\preProcess\\" + "parcellationLhDanielsson.json"
            parcellationJSONFileNameRh = subjectFolder + "\\preProcess\\" + "parcellationRhDanielsson.json"
                        
        labelFileLh = subjectFolder + "\\surfaces\\lh.aparc.annot"
        labelFileRh = subjectFolder + "\\surfaces\\rh.aparc.annot"

        # load precomputed lesion properties
        data = {}

        # Read annotation file Rh.
        labelsRh, ctabRh, regionsRh = freesurfer.read_annot(labelFileRh, orig_ids=False)
        metaRh = dict(
                        (index, {"region": item[0], "color": item[1][:4].tolist()})
                        for index, item in enumerate(zip(regionsRh, ctabRh)))

        # Read annotation file Lh.
        labelsLh, ctabLh, regionsLh = freesurfer.read_annot(labelFileLh, orig_ids=False)
        metaLh = dict(
                        (index, {"region": item[0], "color": item[1][:4].tolist()})
                        for index, item in enumerate(zip(regionsLh, ctabLh)))

        print("Label count Rh " + str(len(labelsRh)))
        print("Label count Lh " + str(len(labelsLh)))

        uniqueLabelsRh = np.unique(labelsRh)
        print(uniqueLabelsRh)
        uniqueLabelsLh = np.unique(labelsLh)
        vertexIdsRh = np.arange(len(labelsRh))
        vertexIdsLh = np.arange(len(labelsLh))

        listOfSegmentedParcellationVerticesRh = []
        for val in uniqueLabelsRh:
            vertices = vertexIdsRh[labelsRh == val]
            listOfSegmentedParcellationVerticesRh.append(vertices)

        listOfSegmentedParcellationVerticesLh = []
        for val in uniqueLabelsLh:
            vertices = vertexIdsLh[labelsLh == val]
            listOfSegmentedParcellationVerticesLh.append(vertices)

        print("Parcellation list count Rh ", len(listOfSegmentedParcellationVerticesRh))
        print("Parcellation list count Lh ", len(listOfSegmentedParcellationVerticesLh))

        #lesionContributionDictRh = dict() # For storing impact patch quantification of all lesions on a single parcellation.
        #lesionContributionDictLh = dict() # For storing impact patch quantification of all lesions on a single parcellation.
        
        # Compute information for Rh hemisphere
        data = {}
        pElementArrayIndex = 0
        r = structureInfo[str(timeIndex)]
        numberOfLesionElements = len(r[0]) # Number of lesion elements at specific time step.
        for pElementIndex in uniqueLabelsRh: # for every parcellation
            #for pElementIndex in range(len(listOfSegmentedParcellationVerticesRh)): # for every parcellation
            lesionImpactData = {}
            lesionContributionQuantified = dict()
            for jsonElementIndex in (range(1,numberOfLesionElements+1)): # for every lesion
                for p in r[0][str(jsonElementIndex)]:
                    if(dataType == "STRUCTURAL"):
                        impactRh = np.array(p["AffectedPointIdsRh"])
                    if(dataType == "DTI"):
                        impactRh = np.array(p["AffectedPointIdsRhDTI"])
                    if(dataType == "DANIELSSON"):
                        impactRh = np.array(p["AffectedPointIdsRhDanielsson"])
                    #print("Type of impactRh", type(impactRh))
                    #print("Type of parcellation verts", type(listOfSegmentedParcellationVerticesRh[pElementIndex]))
                    #print("Length of impactRh", len(impactRh))
                    #print("Length of parcellation verts", len(listOfSegmentedParcellationVerticesRh[pElementIndex]))
                    if impactRh.size>0 and listOfSegmentedParcellationVerticesRh[pElementArrayIndex].size>0:
                        intersectionList = np.intersect1d(impactRh, listOfSegmentedParcellationVerticesRh[pElementArrayIndex])
                        if(intersectionList.size>0):
                            lesionImpactData[jsonElementIndex] = intersectionList.tolist()
                            lesionContributionQuantified.update({'%d'%jsonElementIndex:len(intersectionList.tolist())})
                            #lesionContributionDictRh.update({'%d'%n:lesionContributionQuantified})
                            #print("Intersection")
                        #else:
                            #print("No intersection")
                    #if(np.intersect1d(impactRh, ))
                    #print(impactLh)
            #print(type(lesionImpactData))
            # for item in lesionContributionQuantified:
            #     print("HI SHERIN", item)
            sorted_Contributions = sorted(lesionContributionQuantified.items(), key=operator.itemgetter(1))

            # Prepare data for writing.
            properties={}
            properties['AssociatedLesions'] = lesionImpactData
            properties['LesionInfluenceCount'] = len(lesionImpactData)
            properties['lesionContributionSorted'] = sorted_Contributions
            affectedPoints = []
            for key in lesionImpactData: 
                affectedPoints.extend(lesionImpactData[key])
            uniqueAffectedPoints = np.unique(affectedPoints) 
            properties['PercentageAffected'] = (len(uniqueAffectedPoints)/listOfSegmentedParcellationVerticesRh[pElementArrayIndex].size)*100
            #properties['vertexIdsRh'] = 1
            #properties['NumberOfPixels'] = 2
            data[int(pElementIndex)]=[]
            data[int(pElementIndex)].append(properties)
            pElementArrayIndex = pElementArrayIndex + 1

        dataDictMainRh[timeIndex] = []
        dataDictMainRh[timeIndex].append(data)


        # Compute information for Lh hemisphere
        data = {}
        pElementArrayIndex = 0
        for pElementIndex in uniqueLabelsLh: # for every parcellation
            #for pElementIndex in range(len(listOfSegmentedParcellationVerticesLh)): # for every parcellation
            lesionImpactData = {}
            lesionContributionQuantified = dict()
            for jsonElementIndex in (range(1,numberOfLesionElements+1)): # for every lesion
                for p in r[0][str(jsonElementIndex)]:
                    if(dataType == "STRUCTURAL"):
                        impactLh = np.array(p["AffectedPointIdsLh"])
                    if(dataType == "DTI"):
                        impactLh = np.array(p["AffectedPointIdsLhDTI"])
                    if(dataType == "DANIELSSON"):
                        impactLh = np.array(p["AffectedPointIdsLhDanielsson"])
                    #print("Type of impactRh", type(impactRh))
                    #print("Type of parcellation verts", type(listOfSegmentedParcellationVerticesRh[pElementIndex]))
                    #print("Length of impactRh", len(impactRh))
                    #print("Length of parcellation verts", len(listOfSegmentedParcellationVerticesRh[pElementIndex]))
                    if impactLh.size>0 and listOfSegmentedParcellationVerticesLh[pElementArrayIndex].size>0:
                        intersectionList = np.intersect1d(impactLh, listOfSegmentedParcellationVerticesLh[pElementArrayIndex])
                        if(intersectionList.size>0):
                            lesionImpactData[jsonElementIndex] = intersectionList.tolist()
                            lesionContributionQuantified.update({'%d'%jsonElementIndex:len(intersectionList.tolist())})
                            #print("Intersection")
                        #else:
                            #print("No intersection")
                    #if(np.intersect1d(impactRh, ))
                    #print(impactLh)
            sorted_Contributions = sorted(lesionContributionQuantified.items(), key=operator.itemgetter(1))
            print(sorted_Contributions)
            #print(type(lesionImpactData))
            # Prepare data for writing.
            properties={}
            properties['AssociatedLesions'] = lesionImpactData
            properties['LesionInfluenceCount'] = len(lesionImpactData)
            properties['lesionContributionSorted'] = sorted_Contributions
            affectedPoints = []
            for key in lesionImpactData: 
                affectedPoints.extend(lesionImpactData[key])
            uniqueAffectedPoints = np.unique(affectedPoints) 
            properties['PercentageAffected'] = (len(uniqueAffectedPoints)/listOfSegmentedParcellationVerticesLh[pElementArrayIndex].size)*100
            #properties['vertexIdsRh'] = 1
            #properties['NumberOfPixels'] = 2
            data[int(pElementIndex)]=[]
            data[int(pElementIndex)].append(properties)
            pElementArrayIndex = pElementArrayIndex + 1

        dataDictMainLh[timeIndex] = []
        dataDictMainLh[timeIndex].append(data)
        print("Processed timestep", timeIndex)
    
    # Write parcellation info files.
    with open(parcellationJSONFileNameLh, 'w') as fp:
        json.dump(dataDictMainLh, fp, indent=4)
    # Write parcellation information for Rh hemisphere
    with open(parcellationJSONFileNameRh, 'w') as fp:
        json.dump(dataDictMainRh, fp, indent=4)


rootPath = "D:\\OneDrive - University of Bergen\\Datasets\\MS_Longitudinal\\Subject1\\"
dataCount = 81
#listOfSubjects = ["01016SACH_DATA","01038PAGU_DATA","01039VITE_DATA","01040VANE_DATA","01042GULE_DATA","07001MOEL_DATA","07003SATH_DATA","07010NABO_DATA","07040DORE_DATA","07043SEME_DATA", "08002CHJE_DATA","08027SYBR_DATA","08029IVDI_DATA","08031SEVE_DATA","08037ROGU_DATA"]

# MAIN FUNCTION CALLS.
#ComputeAndWriteParcellationData(dataCount, "STRUCTURAL")
#ComputeAndWriteParcellationData(dataCount, "DTI")
ComputeAndWriteParcellationData(dataCount, "DANIELSSON")
print("COMPLETED SUCCESSFULLY")