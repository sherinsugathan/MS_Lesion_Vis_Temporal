import vtk
import numpy as np
import os
import math
import SimpleITK as sitk
import json


###################################################
####################################################


baselineIndex = 0
followupIndex = 12
#print(baselineIndex, followupIndex)
rootFolder = "D:\\OneDrive - University of Bergen\\Datasets\\MS_Longitudinal\\Subject1\\"
connectedComponentOutputFileName = rootFolder + "lesionMask\\ConnectedComponentsTemp.nii"

# Creating uinion image
maskFileName1 = rootFolder + "lesionMask\\Consensus" + str(baselineIndex) + ".nii"
maskFileName2 = rootFolder + "lesionMask\\Consensus" + str(followupIndex) + ".nii"
niftiReaderLesionMask1 = vtk.vtkNIFTIImageReader()
niftiReaderLesionMask1.SetFileName(maskFileName1)
niftiReaderLesionMask1.Update()
niftiReaderLesionMask2 = vtk.vtkNIFTIImageReader()
niftiReaderLesionMask2.SetFileName(maskFileName2)
niftiReaderLesionMask2.Update()
orImageFilter = vtk.vtkImageLogic()
orImageFilter.SetInput1Data(niftiReaderLesionMask1.GetOutput())
orImageFilter.SetInput2Data(niftiReaderLesionMask2.GetOutput())
orImageFilter.SetOperationToOr()
orImageFilter.Update()
writer = vtk.vtkNIFTIImageWriter()
writer.SetFileName("D:\\union.nii")
writer.SetInputData(orImageFilter.GetOutput())
writer.Write()
# Creating subtracted image
castedImage1 = vtk.vtkImageCast()
castedImage1.SetInputData(niftiReaderLesionMask1.GetOutput())
castedImage1.SetOutputScalarTypeToFloat()
castedImage1.Update()
castedImage2 = vtk.vtkImageCast()
castedImage2.SetInputData(niftiReaderLesionMask2.GetOutput())
castedImage2.SetOutputScalarTypeToFloat()
castedImage2.Update()
subtractImageFilter = vtk.vtkImageMathematics()
subtractImageFilter.SetInput1Data(castedImage1.GetOutput())
subtractImageFilter.SetInput2Data(castedImage2.GetOutput())
subtractImageFilter.SetOperationToSubtract()
subtractImageFilter.Update()
writer.SetFileName("D:\\shr.nii")
writer.SetInputData(subtractImageFilter.GetOutput())
writer.Write()
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
#QFormMatrixMask = niftiReaderLesionMask.GetQFormMatrix()
QFormMatrixMask = niftiReaderLesionMask1.GetQFormMatrix()
qFormListMask = [0] * 16 #the matrix is 4x4
QFormMatrixMask.DeepCopy(qFormListMask, QFormMatrixMask)
transform = vtk.vtkTransform()
transform.Identity()
transform.SetMatrix(qFormListMask)
transform.Update()
print(qFormListMask)
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
    lesionMapper = vtk.vtkOpenGLPolyDataMapper()
    lesionMapper.SetInputData(geometryFilter.GetOutput())
    lesionMapper.Update()   
    probeFilter = vtk.vtkProbeFilter()
    #probeFilter.SetSourceData(niftiReaderDifferenceImage.GetOutput())
    probeFilter.SetSourceData(transformVolumeFilter.GetOutput())
    probeFilter.SetInputData(lesionMapper.GetInput())
    probeFilter.CategoricalDataOff()
    probeFilter.Update()    
    scalars = probeFilter.GetOutput().GetPointData().GetScalars()
    lesionMapper.GetInput().GetPointData().SetActiveScalars("difference")
    lesionMapper.GetInput().GetPointData().SetScalars(scalars)
    lesionMapper.SetScalarRange(-127,127)
    numberOfPoints = scalars.GetNumberOfTuples()
    #transformFilter = vtk.vtkTransformFilter()
    #transformFilter.SetInputData(lesionMapper.GetInput())
    #transformFilter.SetTransform(transform)
    #transformFilter.Update()
    #multiBlockDataset.SetBlock(i,transformFilter.GetOutput())
    multiBlockDataset.SetBlock(i,lesionMapper.GetInput())
nc = vtk.vtkNamedColors()
lut = vtk.vtkLookupTable()
lut.SetNumberOfTableValues(3)
lut.SetTableRange(-128, 128)
lut.Build()
lut.SetTableValue(0,nc.GetColor4d("LightCoral"))
lut.SetTableValue(1,nc.GetColor4d("LightSlateGray"))
lut.SetTableValue(2,nc.GetColor4d("PaleGreen"))
actorList2 = []
for i in range(multiBlockDataset.GetNumberOfBlocks()):
    block = multiBlockDataset.GetBlock(i)
    #newpoly = Utils.smoothPolyData(block)
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputData(block)
    #mapper.SetInputData(newpoly)
    mapper.SetScalarRange(-128,128)
    mapper.SetLookupTable(lut)
    lesionActor = vtk.vtkActor()
    lesionActor.SetMapper(mapper)
    #actorList2.append(lesionActor)

###################################################


rootFolder = "D:\\OneDrive - University of Bergen\\Datasets\\MS_Longitudinal\\Subject1\\surfaces\\lesions\\"
lesionSurfaceDataFilePath = rootFolder + "lesions0.vtm"
mbr = vtk.vtkXMLMultiBlockDataReader()
mbr.SetFileName(lesionSurfaceDataFilePath)
mbr.Update()
mb = mbr.GetOutput()

actorList=[]
for blockIndex in range(mb.GetNumberOfBlocks()):
    polyData = vtk.vtkPolyData.SafeDownCast(mb.GetBlock(blockIndex))
    if polyData and polyData.GetNumberOfPoints():
        mapper = vtk.vtkOpenGLPolyDataMapper()
        mapper.SetInputData(polyData)
        mapper.SetScalarModeToUseCellData()
        mapper.Update()
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(0.7804, 0.4824, 0.4824)
        actor.GetMapper().ScalarVisibilityOff()
        mapper.Update()
        actorList.append(actor)


####################################################

# Visualize
renderer = vtk.vtkRenderer()
renderWindow = vtk.vtkRenderWindow()
renderWindow.AddRenderer(renderer)
renderWindowInteractor = vtk.vtkRenderWindowInteractor()
renderWindowInteractor.SetRenderWindow(renderWindow)
for actor in actorList:
    renderer.AddActor(actor)

for lesion in actorList2:
    renderer.AddActor(lesion)

renderWindow.Render()
renderWindowInteractor.Start()