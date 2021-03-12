
# read lesion voxels, write datashader csv to file and plot datashader graph.
import SimpleITK as sitk
import vtk
import numpy as np
import sys, os
import math
import ctypes
import csv
import datashader as ds, pandas as pd, colorcet
from datashader.utils import export_image

writeCSV = False

if(writeCSV == True):
    rootPath = "D:\\OneDrive - University of Bergen\\Datasets\\MS_Longitudinal\\Subject1\\"
    fileNameT1 = rootPath + "\\structural\\T1.nii"
    fileNameMaskLabels = rootPath + "\\lesionMask\\ConnectedComponents.nii"

    # read and get voxel array from MRI data.
    imageT1 = sitk.ReadImage(fileNameT1)
    imageConnectedComponents = sitk.ReadImage(fileNameMaskLabels)
    dimensions = imageT1.GetSize()
    print("DIMENSIONS", dimensions)

    labelShapeStatisticsFilter = sitk.LabelShapeStatisticsImageFilter()
    labelShapeStatisticsFilter.Execute(imageConnectedComponents)
    labelCount = labelShapeStatisticsFilter.GetNumberOfLabels()
    print("Number of lesion labels", labelCount)
    print("Labels:", labelShapeStatisticsFilter.GetLabels())
    voxelIntensities = {}
    for i in range(1, labelCount+1):
        voxelIntensities[str(i)] = []
    for i in range(dimensions[0]):
        for j in range(dimensions[1]):
            for k in range(dimensions[2]):
                voxelLabel = imageConnectedComponents.GetPixel(i, j, k)
                if(voxelLabel != 0):
                        voxelIntensities[str(voxelLabel)].append(imageT1.GetPixel(i, j, k))

    voxelVector = []
    for elem in voxelIntensities:
        voxelVector = voxelVector + voxelIntensities[elem]

    xDim = len(voxelVector)
    repeatCount = 50
    xVector = list(range(xDim))
    yVector = np.zeros(xDim)

    # first data row of csv file  
    rows = list(zip(xVector, yVector, voxelVector))
    fields = ['x', 'y', 'voxelIntensity']
    # name of csv file  
    filename = "D:\\lesionVoxelIntensities.csv"

    # writing to csv file  
    with open(filename, 'w') as csvfile:  
        # creating a csv writer object  
        csvwriter = csv.writer(csvfile)  
            
        # writing the fields  
        csvwriter.writerow(fields)  
        
        yIndex = 1
        # writing the data rows  
        for i in range(repeatCount):
            csvwriter.writerows(rows)
            yVector = [yIndex] * xDim 
            yIndex = yIndex + 1
            rows = list(zip(xVector, yVector, voxelVector))


# plot
df  = pd.read_csv("D:\\lesionVoxelIntensities.csv")
cvs = ds.Canvas(plot_width=850, plot_height=50)
agg = cvs.points(df, 'x', 'y', ds.mean('voxelIntensity'))
img = ds.tf.shade(agg, cmap=colorcet.fire, how='log')
export_image(img, "lesionVoxels", export_path="D:\\")

