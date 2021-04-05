# intensity normalization for mifti data.
import vtk
import numpy as np
import os
import math
import SimpleITK as sitk
import json
import nibabel as nib
from nibabel.testing import data_path

dataCount = 81
rootFolder = "D:\\OneDrive - University of Bergen\\Datasets\\MS_Longitudinal\\Subject1\\"


for timeStep in range(dataCount):
    #structuralData = rootFolder + "structural\\T1_" + str(timeStep) + ".nii"
    structuralData = "D:\\nu.nii"
    #structuralData = "D:\\test.nii"
    imageT1 = sitk.ReadImage(structuralData)
    n1_img = nib.load(structuralData)
    n1_header = n1_img.header
    print(n1_header)

    #resacleFilter = sitk.RescaleIntensityImageFilter()
    #resacleFilter.SetOutputMaximum(255)
    #resacleFilter.SetOutputMinimum(0)
    #image = resacleFilter.Execute(imageT1)
    #sitk.WriteImage(image,"D:\\test.nii")

    statFilter = sitk.StatisticsImageFilter()
    statFilter.Execute(imageT1)
    print(statFilter.GetMinimum())
    print(statFilter.GetMaximum())
    break