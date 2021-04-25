# This program read the consensus mask data, label lesions them based on connectivity and combines(t0 union t1) previous time point lesion, writes mesh to file.

import vtk
import numpy as np
import os
import math
import SimpleITK as sitk
import json

# Read connected components mask file and perform marching cubes. Write lesion surface as vtm files.
def writeLesionSurfacesAsVTM(timeStep, connectedComponentsMaskFilePath, lesionCount, outputPath, subtractImageFilter):
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

        #print(subtractImageFilter)
        print(lesionMapper.GetInput())
        probeFilter = vtk.vtkProbeFilter()
        probeFilter.SetSourceConnection(subtractImageFilter.GetOutputPort())
        probeFilter.SetInputData(lesionMapper.GetInput())
        probeFilter.Update()    

        scalars = probeFilter.GetOutput().GetPointData().GetScalars()
        numberOfPoints = scalars.GetNumberOfTuples()
        #print(scalars)
        for m in range(numberOfPoints):
            if(scalars.GetTuple(m)[0] != 0.0):
                print("hiii")

        
        #for(int i = 0; i < array->GetNumberOfTuples(); i++)
        #values = array->GetTuple3(i);
        #std::cout << values[0] << " " << values[1] << " " << values[2] << std::endl;


        multiBlockDataset.SetBlock(i,lesionMapper.GetInput())
        print("TIME STEP:", timeStep, "PROCESSING LESION:", i,"/", lesionCount)

    # Write lesions to file.
    mbw = vtk.vtkXMLMultiBlockDataWriter()
    mbw.SetFileName(outputPath + "\\lesionPairCombined"+ str(timeStep) + ".vtm")
    mbw.SetDataModeToAscii()
    mbw.SetInputData(multiBlockDataset)
    mbw.Write()
    print("FILE WRITTEN SUCCESSFULLY")

def LesionDataWriter():
    rootFolder = "D:\\OneDrive - University of Bergen\\Datasets\\MS_Longitudinal\\Subject1\\"
    dataCount = 81

    dataDictMain = {}
    for i in range(0, dataCount, 2):
        maskFileName1 = rootFolder + "lesionMask\\Consensus" + str(i) + ".nii"
        maskFileName2 = rootFolder + "lesionMask\\Consensus" + str(i+50) + ".nii"
        connectedComponentOutputFileName = rootFolder + "lesionMask\\ConnectedComponentsTemp.nii"
        lesionVTMSurfacesOutputPath = rootFolder + "\\surfaces\\lesionsComparison\\"
        lesionPairComparisonLabelMaskVolumePath = rootFolder + "\\surfaces\\lesionsComparison\\lesionPairComparisonLabelMask"+ str(i) +".nii"
        
        #imageLesionMask1 = sitk.ReadImage(maskFileName1)
        #imageLesionMask2 = sitk.ReadImage(maskFileName2)
        niftiReaderLesionMask1 = vtk.vtkNIFTIImageReader()
        niftiReaderLesionMask1.SetFileName(maskFileName1)
        niftiReaderLesionMask1.Update()
        niftiReaderLesionMask2 = vtk.vtkNIFTIImageReader()
        niftiReaderLesionMask2.SetFileName(maskFileName2)
        niftiReaderLesionMask2.Update()
        print("done1")
        #castImageFilter = sitk.CastImageFilter() # This is needed for performing A-B and B-A
        #castImageFilter.SetOutputPixelType(sitk.sitkFloat32)
        #castedImage1 = castImageFilter.Execute(imageLesionMask1)
        #castedImage2 = castImageFilter.Execute(imageLesionMask2)
        castedImage1 = vtk.vtkImageCast()
        castedImage1.SetInputData(niftiReaderLesionMask1.GetOutput())
        castedImage1.SetOutputScalarTypeToFloat()
        castedImage1.Update()
        castedImage2 = vtk.vtkImageCast()
        castedImage2.SetInputData(niftiReaderLesionMask2.GetOutput())
        castedImage2.SetOutputScalarTypeToFloat()
        castedImage2.Update()
        print("done2")

        # Combined mask/mesh
        #orImageFilter = sitk.OrImageFilter()
        #AunionB = orImageFilter.Execute(imageLesionMask1, imageLesionMask2)
        #sitk.WriteImage(AunionB, lesionPairComparisonLabelMaskVolumePath)
        orImageFilter = vtk.vtkImageLogic()
        orImageFilter.SetInput1Data(niftiReaderLesionMask1.GetOutput())
        orImageFilter.SetInput2Data(niftiReaderLesionMask2.GetOutput())
        orImageFilter.SetOperationToOr()
        orImageFilter.Update()
        writer = vtk.vtkNIFTIImageWriter()
        writer.SetFileName("D:\\union.nii")
        writer.SetInputData(orImageFilter.GetOutput())
        writer.Write()

        # Compute difference between pair.
        #subtractImageFilter = sitk.SubtractImageFilter()
        #AminusB = subtractImageFilter.Execute(castedImage1, castedImage2)
        #sitk.WriteImage(AminusB, "D:\\aminusb.nii")
        subtractImageFilter = vtk.vtkImageMathematics()
        subtractImageFilter.SetInput1Data(castedImage1.GetOutput())
        subtractImageFilter.SetInput2Data(castedImage2.GetOutput())
        subtractImageFilter.SetOperationToSubtract()
        subtractImageFilter.Update()
        print("done3")
        writer.SetFileName("D:\\shr.nii")
        writer.SetInputData(subtractImageFilter.GetOutput())
        writer.Write()

        # Connected component filter.
        uinionImage = sitk.ReadImage("D:\\union.nii")
        connectedComponentFilter = sitk.ConnectedComponentImageFilter()
        connectedComponentImage = connectedComponentFilter.Execute(uinionImage)
        sitk.WriteImage(connectedComponentImage, connectedComponentOutputFileName)
        objectCount = connectedComponentFilter.GetObjectCount()
        print(objectCount)

        # Write lesion surfaces as VTM
        writeLesionSurfacesAsVTM(i, connectedComponentOutputFileName, objectCount, lesionVTMSurfacesOutputPath, subtractImageFilter)



        #BminusA = subtractImageFilter.Execute(castedImage2, castedImage1)
        #sitk.WriteImage(BminusA, "D:\\bminusa.nii")
        quit()





        print("Completed processing Instance:" + str(i) + ", " + str(i+1) + " Lesions found:" + str(objectCount))

    print("2. LesionComparisonDataWriter() Completed successfully")


LesionDataWriter()