# This program read the consensus mask data, label lesions them based on connectivity and writes lesion statistics to json file.

import vtk
import numpy as np
import os
import math
import SimpleITK as sitk
import json

# Read connected components mask file and perform marching cubes. Write lesion surface as vtm files.
def writeLesionSurfacesAsVTM(timeStep, connectedComponentsMaskFilePath, lesionCount, outputPath):
    # Load lesion mask
    niftiReaderLesionMask = vtk.vtkNIFTIImageReader()
    niftiReaderLesionMask.SetFileName(connectedComponentsMaskFilePath)
    niftiReaderLesionMask.Update()

    # Read QForm matrix from mask data.
    QFormMatrixMask = niftiReaderLesionMask.GetQFormMatrix()
    qFormListMask = [0] * 16 #the matrix is 4x4
    QFormMatrixMask.DeepCopy(qFormListMask, QFormMatrixMask)

    surface = vtk.vtkDiscreteMarchingCubes()
    surface.SetInputConnection(niftiReaderLesionMask.GetOutputPort())
    for i in range(lesionCount):
        surface.SetValue(i,i+1)
    surface.Update()

    transform = vtk.vtkTransform()
    transform.Identity()
    transform.SetMatrix(qFormListMask)
    transform.Update()
    transformFilter = vtk.vtkTransformFilter()
    transformFilter.SetInputConnection(surface.GetOutputPort())
    transformFilter.SetTransform(transform)
    transformFilter.Update()

    multiBlockDataset = vtk.vtkMultiBlockDataSet()

    for i in range(lesionCount):
        threshold = vtk.vtkThreshold()
        threshold.SetInputData(transformFilter.GetOutput())
        threshold.ThresholdBetween(i+1,i+1)
        threshold.Update()

        geometryFilter = vtk.vtkGeometryFilter()
        geometryFilter.SetInputData(threshold.GetOutput())
        geometryFilter.Update()

        lesionMapper = vtk.vtkOpenGLPolyDataMapper()
        lesionMapper.SetInputConnection(geometryFilter.GetOutputPort())
        lesionMapper.Update()       

        multiBlockDataset.SetBlock(i,lesionMapper.GetInput())
        print("TIME STEP:", timeStep, "PROCESSING LESION:", i,"/", lesionCount)

    # Write lesions to file.
    mbw = vtk.vtkXMLMultiBlockDataWriter()
    mbw.SetFileName(outputPath + "\\lesions"+ str(timeStep) + ".vtm")
    mbw.SetDataModeToAscii()
    mbw.SetInputData(multiBlockDataset)
    mbw.Write()
    print("FILE WRITTEN SUCCESSFULLY")




def LesionDataWriter():
    #rootFolder = "D:\\OneDrive - University of Bergen\\Datasets\\MS_Longitudinal\\Subject1\\"
    rootFolder = "D:\\OneDrive - University of Bergen\\Datasets\\MS_Longitudinal\\Subj2_1_MS_DTI\\"

    #dataCount = 81
    dataCount = 2

    dataDictMain = {}
    for i in range(dataCount):
        maskFileName = rootFolder + "lesionMask\\Consensus" + str(i) + ".nii"
        connectedComponentOutputFileName = rootFolder + "lesionMask\\ConnectedComponents.nii"
        lesionVTMSurfacesOutputPath = rootFolder + "\\surfaces\\lesions\\"
        imageLesionMask = sitk.ReadImage(maskFileName)


        if("float" in imageLesionMask.GetPixelIDTypeAsString()):
            print("Converting float to integer...")
            castImageFilter = sitk.CastImageFilter()
            castImageFilter.SetOutputPixelType(sitk.sitkUInt8)
            imageLesionMask = castImageFilter.Execute(imageLesionMask)

        # Connected component filter.
        connectedComponentFilter = sitk.ConnectedComponentImageFilter()
        connectedComponentImage = connectedComponentFilter.Execute(imageLesionMask)
        sitk.WriteImage(connectedComponentImage, connectedComponentOutputFileName)
        objectCount = connectedComponentFilter.GetObjectCount()

        # Label statistics filter.
        labelShapeStatisticsFilter = sitk.LabelShapeStatisticsImageFilter()
        labelShapeStatisticsFilter.Execute(connectedComponentImage)

        # extract individual values and store in central database (for this participant)
        dataDictLesion = {}
        for u in range(1,labelShapeStatisticsFilter.GetNumberOfLabels()+1):
            properties={}
            properties['Elongation'] = labelShapeStatisticsFilter.GetElongation(u)
            properties['NumberOfPixels'] = labelShapeStatisticsFilter.GetNumberOfPixels(u)
            properties['NumberOfPixelsOnBorder'] = labelShapeStatisticsFilter.GetNumberOfPixelsOnBorder(u)
            properties['Centroid'] = labelShapeStatisticsFilter.GetCentroid(u)
            properties['BoundingBox'] = labelShapeStatisticsFilter.GetBoundingBox(u)
            properties['EllipsoidDiameter'] = labelShapeStatisticsFilter.GetEquivalentEllipsoidDiameter(u)
            properties['SphericalPerimeter'] = labelShapeStatisticsFilter.GetEquivalentSphericalPerimeter(u)        
            properties['SphericalRadius'] = labelShapeStatisticsFilter.GetEquivalentSphericalRadius(u)
            properties['FeretDiameter'] = labelShapeStatisticsFilter.GetFeretDiameter(u)
            properties['Flatness'] = labelShapeStatisticsFilter.GetFlatness(u)
            properties['Perimeter'] = labelShapeStatisticsFilter.GetPerimeter(u)
            properties['PerimeterOnBorder'] = labelShapeStatisticsFilter.GetPerimeterOnBorder(u)
            properties['PerimeterOnBorderRatio'] = labelShapeStatisticsFilter.GetPerimeterOnBorderRatio(u)
            properties['PhysicalSize'] = labelShapeStatisticsFilter.GetPhysicalSize(u)
            properties['PrincipalAxes'] = labelShapeStatisticsFilter.GetPrincipalAxes(u)
            properties['PrincipalMoments'] = labelShapeStatisticsFilter.GetPrincipalMoments(u)
            properties['Region'] = labelShapeStatisticsFilter.GetRegion(u)
            properties['Roundness'] = labelShapeStatisticsFilter.GetRoundness(u)

            dataDictLesion[u]=[]
            dataDictLesion[u].append(properties)

        dataDictMain[i]=[]
        dataDictMain[i].append(dataDictLesion)

        # Write lesion surfaces as VTM
        writeLesionSurfacesAsVTM(i, connectedComponentOutputFileName, objectCount, lesionVTMSurfacesOutputPath)

        print("Completed processing Instance:" + str(i) + " " + " Lesions found:" + str(objectCount))

    # now store the data structure for the program to use
    with open(rootFolder + "preProcess\\lesionStatistics.json", "w") as fp:
        json.dump(dataDictMain, fp, indent=4)
    print("2. LesionDataWriter() Completed successfully")


LesionDataWriter()