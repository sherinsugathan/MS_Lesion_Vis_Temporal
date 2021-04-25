import vtk
import numpy as np
import os
import math
import SimpleITK as sitk
import json

rootFolder = "D:\\OneDrive - University of Bergen\\Datasets\\MS_Longitudinal\\Subject1\\"
connectedComponentOutputFileName = rootFolder + "lesionMask\\ConnectedComponentsTemp.nii"

uinionImage = sitk.ReadImage("D:\\union.nii")
connectedComponentFilter = sitk.ConnectedComponentImageFilter()
connectedComponentImage = connectedComponentFilter.Execute(uinionImage)
sitk.WriteImage(connectedComponentImage, connectedComponentOutputFileName)
lesionCount = connectedComponentFilter.GetObjectCount()

# Load lesion mask
niftiReaderLesionMask = vtk.vtkNIFTIImageReader()
niftiReaderLesionMask.SetFileName(connectedComponentOutputFileName)
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

# Load lesion mask
niftiReaderDifferenceImage = vtk.vtkNIFTIImageReader()
niftiReaderDifferenceImage.SetFileName("D:\\shr.nii")
niftiReaderDifferenceImage.Update()

transformVolumeFilter = vtk.vtkTransformFilter()
transformVolumeFilter.SetInputConnection(niftiReaderDifferenceImage.GetOutputPort())
transformVolumeFilter.SetTransform(transform)
transformVolumeFilter.Update()

multiBlockDataset = vtk.vtkMultiBlockDataSet()
for i in range(lesionCount):
    threshold = vtk.vtkThreshold()
    #threshold.SetInputData(surface.GetOutput())
    threshold.SetInputData(transformFilter.GetOutput())
    threshold.ThresholdBetween(i+1,i+1)
    threshold.Update()
    geometryFilter = vtk.vtkGeometryFilter()
    geometryFilter.SetInputData(threshold.GetOutput())
    geometryFilter.Update()

    #triangleFilter = vtk.vtkTriangleFilter()
    #triangleFilter.SetInputData(geometryFilter.GetOutput())
    #triangleFilter.Update()
    lesionMapper = vtk.vtkOpenGLPolyDataMapper()
    lesionMapper.SetInputData(geometryFilter.GetOutput())
    lesionMapper.Update()   
    #print(subtractImageFilter)


    #print(lesionMapper.GetInput())
    probeFilter = vtk.vtkProbeFilter()
    #probeFilter.SetSourceData(niftiReaderDifferenceImage.GetOutput())
    probeFilter.SetSourceData(transformVolumeFilter.GetOutput())
    probeFilter.SetInputData(lesionMapper.GetInput())
    probeFilter.CategoricalDataOff()
    probeFilter.Update()    
    #print(probeFilter.GetValidPoints())
    scalars = probeFilter.GetOutput().GetPointData().GetScalars()
    lesionMapper.GetInput().GetPointData().SetActiveScalars("difference")
    lesionMapper.GetInput().GetPointData().SetScalars(scalars)
    lesionMapper.SetScalarRange(-127,127)
    #print(lesionMapper.GetScalarRange())

    numberOfPoints = scalars.GetNumberOfTuples()
    #print(scalars)
    # for m in range(numberOfPoints):
    #     #print(scalars.GetTuple(m)[0])
    #     if(scalars.GetTuple(m)[0] < 0.0):
    #         print(scalars.GetTuple(m)[0])
    #         #print("hiii255")

    multiBlockDataset.SetBlock(i,lesionMapper.GetInput())

nc = vtk.vtkNamedColors()

lut = vtk.vtkLookupTable()
lut.SetNumberOfTableValues(3)
lut.SetTableRange(-128, 128)
lut.Build()

# Fill in a few known colors, the rest will be generated if needed

# for i in range(-128,-1):
#     lut.SetTableValue(i + 128, 1.0, 0.0, 0.0, 1.0)
# i = i + 1
# lut.SetTableValue(i + 128, 0.0, 0.1, 0.0, 1.0)
# for i in range(1,128):
#     lut.SetTableValue(i + 128, 0.0, 0.0, 1.0, 1.0)




lut.SetTableValue(0,nc.GetColor4d("PaleGreen"))
lut.SetTableValue(1,nc.GetColor4d("LightSlateGray"))
lut.SetTableValue(2,nc.GetColor4d("LightCoral"))

actorList = []
for i in range(multiBlockDataset.GetNumberOfBlocks()):
    block = multiBlockDataset.GetBlock(i)
    #print(block)
    print(block.GetScalarRange())
    
    #block.GetPointData().SetActiveScalars("difference")
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputData(block)
    mapper.SetScalarRange(-128,128)
    mapper.SetLookupTable(lut)
    lesionActor = vtk.vtkActor()
    lesionActor.SetMapper(mapper)
    actorList.append(lesionActor)


# Visualize
renderer = vtk.vtkRenderer()
renderWindow = vtk.vtkRenderWindow()
renderWindow.AddRenderer(renderer)
renderWindowInteractor = vtk.vtkRenderWindowInteractor()
renderWindowInteractor.SetRenderWindow(renderWindow)
for actor in actorList:
    renderer.AddActor(actor)
renderWindow.Render()
renderWindowInteractor.Start()

