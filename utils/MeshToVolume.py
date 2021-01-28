# Read blender generated lesion surface files and create binary mask volumes data from it. Uses existing consensus data for a reference.

import vtk
import numpy as np
import os
import math
import SimpleITK as sitk

def MeshToVolume():
    rootFolder = "D:\\OneDrive - University of Bergen\\Datasets\\MS_SegmentationChallengeDataset\\DTIDATA\\"
    referenceMaskDataVolume = rootFolder + "\\lesionMask\\Consensus.nii"
    dataCount = 81

    for i in range(dataCount):
        lesionMeshFileName = "D:\\OneDrive - University of Bergen\\Datasets\\MS_Longitudinal\\Subject1\\surfaces\\lesions\\l" + str(i) + ".obj"
        outputFileName = "D:\\OneDrive - University of Bergen\\Datasets\\MS_Longitudinal\\Subject1\\lesionMask\\Consensus" + str(i) + ".nii"
        
        objReader = vtk.vtkOBJReader()
        objReader.SetFileName(lesionMeshFileName)
        objReader.Update()
        
        # Read reference mask image.
        niftyReaderMask = vtk.vtkNIFTIImageReader() 
        niftyReaderMask.SetFileName(referenceMaskDataVolume)
        niftyReaderMask.Update()
        
        lesionPolyData=objReader.GetOutput()
        
        niftyImage = niftyReaderMask.GetOutput()
        # print("BOUNDS", niftyImage.GetBounds())
        # print("ORIGIN", niftyImage.GetOrigin())
        # print("DIMENSIONS", niftyImage.GetDimensions())
        # print("DIRECTION MATRIX", niftyImage.GetIndexToPhysicalMatrix())
        
        spacing = [0] * 3  # desired volume spacing
        spacing[0] = 0.7
        spacing[1] = 0.7
        spacing[2] = 0.7
        #bounds = [0]*6
        #lesionPolyData.GetBounds(bounds)
        bounds=niftyImage.GetBounds()
        
        lesionVolumeImage = vtk.vtkImageData()
        lesionVolumeImage.SetSpacing(spacing)
        streamDims = [0]*3
        niftyImage.GetDimensions(streamDims)
        
        # for i in range(3):
        #     streamDims[i] = int(math.ceil((bounds[i * 2 + 1] - bounds[i * 2]) / spacing[i]))
        lesionVolumeImage.SetDimensions(streamDims)
        lesionVolumeImage.SetExtent(0, streamDims[0] - 1, 0, streamDims[1] - 1, 0, streamDims[2] - 1)
        streamOrigin = [0]*3
        streamOrigin[0] = bounds[0] + spacing[0] / 2
        streamOrigin[1] = bounds[2] + spacing[1] / 2
        streamOrigin[2] = bounds[4] + spacing[2] / 2
        #streamOrigin=niftyImage.GetOrigin()
        lesionVolumeImage.SetOrigin(streamOrigin)
        lesionVolumeImage.AllocateScalars(vtk.VTK_UNSIGNED_CHAR, 1)
        
        inVal = 255
        outVal = 0
        count = lesionVolumeImage.GetNumberOfPoints()
        for i in range(count):
            lesionVolumeImage.GetPointData().GetScalars().SetTuple1(i, inVal)
        pol2stencil = vtk.vtkPolyDataToImageStencil()
        pol2stencil.SetInputData(lesionPolyData)
        pol2stencil.SetOutputOrigin(streamOrigin)
        pol2stencil.SetOutputSpacing(spacing)
        pol2stencil.SetOutputWholeExtent(lesionVolumeImage.GetExtent())
        pol2stencil.Update()
        imgStencil = vtk.vtkImageStencil()
        imgStencil.SetInputData(lesionVolumeImage)
        imgStencil.SetStencilConnection(pol2stencil.GetOutputPort())
        imgStencil.ReverseStencilOff()
        imgStencil.SetBackgroundValue(outVal)
        imgStencil.Update()
        
        niftiWriter = vtk.vtkNIFTIImageWriter()
        niftiWriter.SetInputConnection(imgStencil.GetOutputPort())
        # copy most information directoy from the header
        niftiWriter.SetNIFTIHeader(niftyReaderMask.GetNIFTIHeader())
        # this information will override the reader's header
        niftiWriter.SetQFac(niftyReaderMask.GetQFac())
        niftiWriter.SetTimeDimension(niftyReaderMask.GetTimeDimension())
        niftiWriter.SetQFormMatrix(niftyReaderMask.GetQFormMatrix())
        niftiWriter.SetSFormMatrix(niftyReaderMask.GetSFormMatrix())
        niftiWriter.SetFileName(outputFileName)
        niftiWriter.Write()
        print("Finished processing data instance", i)    
    print("1. MeshToVolume() Successfully completed")

