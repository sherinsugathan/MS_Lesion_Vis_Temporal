# Using lesion mask and structural data, write intensity statistics(mean, median, variance, std etc.) to json file.
import vtk
import numpy as np
import os
import math
import SimpleITK as sitk
import json

def IntensityStatisticsWriter():
    rootFolder = "D:\\OneDrive - University of Bergen\\Datasets\\MS_Longitudinal\\Subject1\\"
    dataCount = 81
    for i in range(dataCount):
        maskFileName = rootFolder + "lesionMask\\Consensus" + str(i) + ".nii"
        structuralData = rootFolder + 
