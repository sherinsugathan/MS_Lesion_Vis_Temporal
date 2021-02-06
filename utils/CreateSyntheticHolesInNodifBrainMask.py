# This program create holes in nodif_brain_mask using the synthetic lesion Consensus mask.
import vtk
import numpy as np
import os
import math
import SimpleITK as sitk

def CreateSyntheticHolesInNodifBrainMask():
    rootFolder = "D:\\OneDrive - University of Bergen\\Datasets\\MS_Longitudinal\\Subject1\\"
    #rootPath = os.path.dirname(os.path.realpath(__file__))
    nodifBrainMaskFile = rootFolder + "\\structural\\nodif_brain_mask.nii"
    dataCount = 81
    lesionVoxelValue = 255 # lesion voxel value inside lesion mask.
    #lesionVoxelValue = 255 # lesion voxel value inside lesion mask.

    niftiReader = vtk.vtkNIFTIImageReader()
    niftiReader.SetFileName(nodifBrainMaskFile)
    niftiReader.Update()

    readerBrainMask = sitk.ImageFileReader()
    readerBrainMask.SetFileName(nodifBrainMaskFile)
    readerBrainMask.LoadPrivateTagsOn()
    readerBrainMask.ReadImageInformation()
    readerBrainMask.LoadPrivateTagsOn()
    imageBrainMask = sitk.ReadImage(nodifBrainMaskFile)

    for dataIndex in range(dataCount):
        consensusLesionMaskFile = rootFolder + "lesionMask\\Consensus" + str(dataIndex) + ".nii"

        readerLesionHoles = sitk.ImageFileReader()
        readerLesionHoles.SetFileName(consensusLesionMaskFile)
        readerLesionHoles.LoadPrivateTagsOn()
        readerLesionHoles.ReadImageInformation()
        readerLesionHoles.LoadPrivateTagsOn()
        imageHoles = sitk.ReadImage(consensusLesionMaskFile)

        #brainMaskArray = sitk.GetArrayFromImage(imageBrainMask)
        lesionHolesArray = sitk.GetArrayFromImage(imageHoles)
        # print(lesionHolesArray.shape[0])
        # print(lesionHolesArray.shape[1])
        # print(lesionHolesArray.shape[2])

        for i in range(lesionHolesArray.shape[0]):
            for j in range(lesionHolesArray.shape[1]):
                for k in range(lesionHolesArray.shape[2]):
                    if(imageHoles[i,j,k]==lesionVoxelValue):
                            pt = imageHoles.TransformIndexToPhysicalPoint((i,j,k))
                            index = imageBrainMask.TransformPhysicalPointToIndex(pt)
                            imageBrainMask[index[0], index[1], index[2]] = 0 

        sitk.WriteImage(imageBrainMask, "D:\\temp\\nodif_brain_mask" + str(dataIndex) + ".nii")
        print("iteration", dataIndex)

    print("CreateSyntheticHolesInNodifBrainMask() SUCCESSFULLY COMPLETED")